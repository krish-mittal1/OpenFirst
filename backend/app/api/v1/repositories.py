
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.dependencies import get_cache, get_db
from app.schemas.repository import RepositoryQueryParams
from app.services import repository_service

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.get("")
async def list_repositories(
    language: str | None = Query(None, description="Filter by primary language"),
    min_stars: int | None = Query(None, ge=0, description="Minimum star count"),
    max_stars: int | None = Query(None, ge=0, description="Maximum star count"),
    min_activity_score: float | None = Query(None, ge=0, le=100),
    min_bf_score: float | None = Query(None, ge=0, le=100),
    sort_by: str = Query("combined_score", pattern="^(combined_score|activity_score|beginner_friendliness_score|stars|last_commit_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    search: str | None = Query(None, description="Search name and description"),
    topics: str | None = Query(None, description="Comma-separated topic filter"),
    has_issues: bool | None = Query(None, description="Must have open good-first-issues"),
    actively_merging: bool | None = Query(None, description="Only show actively merging repos"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    params = RepositoryQueryParams(
        language=language,
        min_stars=min_stars,
        max_stars=max_stars,
        min_activity_score=min_activity_score,
        min_bf_score=min_bf_score,
        sort_by=sort_by,
        order=order,
        search=search,
        topics=topics,
        has_issues=has_issues,
        actively_merging=actively_merging,
        page=page,
        per_page=per_page,
    )
    return await repository_service.get_repositories(db, cache, params)


@router.get("/live-search")
async def live_search_repositories(
    q: str = Query(..., min_length=2, description="Search query for GitHub"),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    from app.services.github_client import github_client
    from app.services.github_sync import sync_single_repo

    try:
        result = await github_client.search_repositories(
            query=f"{q} stars:>10 archived:false",
            sort="stars",
            order="desc",
            per_page=per_page,
            page=1,
        )
        items = result.get("items", [])
        if not items:
            return {"data": [], "source": "github", "total": 0}

        synced_repos = []
        for repo_data in items[:per_page]:
            try:
                repo = await sync_single_repo(db, repo_data)
                if repo:
                    synced_repos.append({
                        "id": repo.id,
                        "full_name": repo.full_name,
                        "description": repo.description,
                        "primary_language": repo.primary_language,
                        "stars": repo.stars,
                        "forks": repo.forks,
                        "topics": repo.topics if isinstance(repo.topics, list) else [],
                        "scores": {
                            "activity": round(repo.activity_score, 1),
                            "beginner_friendliness": round(repo.beginner_friendliness_score, 1),
                            "combined": round(repo.combined_score, 1),
                        },
                        "metrics": {
                            "good_first_issue_count": repo.good_first_issue_count,
                            "contributor_count": repo.contributor_count,
                            "avg_pr_merge_hours": repo.avg_pr_merge_hours,
                            "last_commit_at": repo.last_commit_at.isoformat() if repo.last_commit_at else None,
                        },
                    })
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Live sync failed for %s: %s", repo_data.get("full_name"), e)
                continue

        return {
            "data": synced_repos,
            "source": "github",
            "total": len(synced_repos),
        }
    except Exception as e:
        return {"data": [], "source": "github", "error": str(e), "total": 0}


@router.get("/{repo_id}")
async def get_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    return await repository_service.get_repository_by_id(db, cache, repo_id)


@router.get("/{repo_id}/issues")
async def get_repository_issues(
    repo_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    from app.schemas.issue import IssueQueryParams
    from app.services import issue_service

    from sqlalchemy import select, func
    from app.models.issue import Issue

    cache_key = f"repos:{repo_id}:issues:{page}"

    async def _fetch():
        import math

        count_stmt = select(func.count(Issue.id)).where(
            Issue.repo_id == repo_id,
            Issue.is_good_first_issue == True,  # noqa
            Issue.state == "open",
        )
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Issue)
            .where(
                Issue.repo_id == repo_id,
                Issue.is_good_first_issue == True,  # noqa
                Issue.state == "open",
            )
            .order_by(Issue.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await db.execute(stmt)
        issues = result.scalars().all()

        return {
            "data": [
                {
                    "id": i.id,
                    "github_id": i.github_id,
                    "title": i.title,
                    "body_preview": (i.body_preview or "")[:200],
                    "html_url": i.html_url,
                    "labels": i.labels if isinstance(i.labels, list) else [],
                    "comment_count": i.comment_count,
                    "difficulty_estimate": i.difficulty_estimate,
                    "is_assigned": i.is_assigned,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                }
                for i in issues
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total,
                "total_pages": math.ceil(total / per_page) if total else 0,
            },
        }

    from app.config import settings
    return await cache.get_or_set(cache_key, settings.cache_ttl_issues, _fetch)


@router.get("/{repo_id}/metrics-history")
async def get_metrics_history(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    return await repository_service.get_repo_metrics_history(db, cache, repo_id)
