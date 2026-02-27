
from __future__ import annotations

import logging
import math
from typing import Any

from sqlalchemy import Select, func, select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.cache import CacheService
from app.core.exceptions import NotFoundError
from app.models.issue import Issue
from app.models.language import RepoLanguage
from app.models.metrics_history import RepoMetricsHistory
from app.models.repository import Repository
from app.schemas.repository import (
    IssueBrief,
    RepoLanguageOut,
    RepoMetrics,
    RepoScores,
    RepositoryDetail,
    RepositoryListItem,
    RepositoryQueryParams,
)

logger = logging.getLogger(__name__)


def _apply_filters(stmt: Select, params: RepositoryQueryParams) -> Select:
    stmt = stmt.where(Repository.is_active == True)  # noqa: E712

    if params.language:
        stmt = stmt.where(Repository.primary_language.ilike(params.language))
    if params.min_stars is not None:
        stmt = stmt.where(Repository.stars >= params.min_stars)
    if params.max_stars is not None:
        stmt = stmt.where(Repository.stars <= params.max_stars)
    if params.min_activity_score is not None:
        stmt = stmt.where(Repository.activity_score >= params.min_activity_score)
    if params.min_bf_score is not None:
        stmt = stmt.where(
            Repository.beginner_friendliness_score >= params.min_bf_score
        )
    if params.has_issues:
        stmt = stmt.where(Repository.good_first_issue_count > 0)
    if params.search:
        pattern = f"%{params.search}%"
        stmt = stmt.where(
            or_(
                Repository.full_name.ilike(pattern),
                Repository.description.ilike(pattern),
            )
        )
    if params.topic_list:
        for topic in params.topic_list:
            stmt = stmt.where(
                cast(Repository.topics, String).ilike(f"%{topic}%")
            )
    if params.actively_merging:
        stmt = stmt.where(Repository.is_actively_merging == True)  # noqa

    return stmt


def _apply_sorting(stmt: Select, params: RepositoryQueryParams) -> Select:
    sort_map = {
        "combined_score": Repository.combined_score,
        "activity_score": Repository.activity_score,
        "beginner_friendliness_score": Repository.beginner_friendliness_score,
        "stars": Repository.stars,
        "last_commit_at": Repository.last_commit_at,
    }
    col = sort_map.get(params.sort_by, Repository.combined_score)
    if params.order == "asc":
        stmt = stmt.order_by(col.asc().nulls_last())
    else:
        stmt = stmt.order_by(col.desc().nulls_last())
    return stmt


def _repo_to_list_item(repo: Repository) -> dict:
    total_prs = repo.merged_pr_count + repo.closed_pr_count
    return {
        "id": repo.id,
        "full_name": repo.full_name,
        "description": repo.description,
        "primary_language": repo.primary_language,
        "stars": repo.stars,
        "forks": repo.forks,
        "license": repo.license,
        "topics": repo.topics if isinstance(repo.topics, list) else [],
        "scores": {
            "activity": repo.activity_score,
            "beginner_friendliness": repo.beginner_friendliness_score,
            "combined": repo.combined_score,
        },
        "metrics": {
            "last_commit_at": repo.last_commit_at.isoformat() if repo.last_commit_at else None,
            "avg_pr_merge_hours": repo.avg_pr_merge_hours,
            "avg_issue_response_hours": repo.avg_issue_response_hours,
            "contributor_count": repo.contributor_count,
            "open_pr_count": repo.open_pr_count,
            "closed_pr_count": repo.closed_pr_count,
            "merged_pr_count": repo.merged_pr_count,
            "good_first_issue_count": repo.good_first_issue_count,
        },
        "synced_at": repo.synced_at.isoformat() if repo.synced_at else None,
        "is_actively_merging": repo.is_actively_merging,
        "pr_merge_rate": repo.pr_merge_rate,
    }


async def get_repositories(
    db: AsyncSession,
    cache: CacheService,
    params: RepositoryQueryParams,
) -> dict[str, Any]:
    cache_key = f"repos:list:{CacheService.hash_params(params.model_dump())}"

    async def _fetch():
        count_stmt = select(func.count(Repository.id))
        count_stmt = _apply_filters(count_stmt, params)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = select(Repository)
        stmt = _apply_filters(stmt, params)
        stmt = _apply_sorting(stmt, params)
        stmt = stmt.offset(params.offset).limit(params.per_page)

        result = await db.execute(stmt)
        repos = result.scalars().all()

        return {
            "data": [_repo_to_list_item(r) for r in repos],
            "pagination": {
                "page": params.page,
                "per_page": params.per_page,
                "total_items": total,
                "total_pages": math.ceil(total / params.per_page) if total else 0,
            },
        }

    return await cache.get_or_set(cache_key, settings.cache_ttl_repo_list, _fetch)


async def get_repository_by_id(
    db: AsyncSession,
    cache: CacheService,
    repo_id: int,
) -> dict[str, Any]:
    cache_key = f"repos:detail:{repo_id}"

    async def _fetch():
        stmt = (
            select(Repository)
            .where(Repository.id == repo_id)
            .options(
                selectinload(Repository.languages),
                selectinload(Repository.issues),
            )
        )
        result = await db.execute(stmt)
        repo = result.scalar_one_or_none()

        if repo is None:
            raise NotFoundError("Repository", str(repo_id))

        total_prs = repo.merged_pr_count + repo.closed_pr_count

        gfi_stmt = (
            select(Issue)
            .where(Issue.repo_id == repo_id, Issue.is_good_first_issue == True, Issue.state == "open")  # noqa
            .order_by(Issue.created_at.desc())
            .limit(10)
        )
        gfi_result = await db.execute(gfi_stmt)
        gfis = gfi_result.scalars().all()

        return {
            "id": repo.id,
            "full_name": repo.full_name,
            "owner": repo.owner,
            "name": repo.name,
            "description": repo.description,
            "primary_language": repo.primary_language,
            "stars": repo.stars,
            "forks": repo.forks,
            "open_issues_count": repo.open_issues_count,
            "watchers": repo.watchers,
            "license": repo.license,
            "topics": repo.topics if isinstance(repo.topics, list) else [],
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "scores": {
                "activity": repo.activity_score,
                "beginner_friendliness": repo.beginner_friendliness_score,
                "combined": repo.combined_score,
            },
            "metrics": {
                "last_commit_at": repo.last_commit_at.isoformat() if repo.last_commit_at else None,
                "last_pushed_at": repo.last_pushed_at.isoformat() if repo.last_pushed_at else None,
                "avg_pr_merge_hours": repo.avg_pr_merge_hours,
                "avg_issue_response_hours": repo.avg_issue_response_hours,
                "contributor_count": repo.contributor_count,
                "open_pr_count": repo.open_pr_count,
                "closed_pr_count": repo.closed_pr_count,
                "merged_pr_count": repo.merged_pr_count,
                "open_closed_pr_ratio": round(repo.open_pr_count / total_prs, 3) if total_prs else None,
                "good_first_issue_count": repo.good_first_issue_count,
            },
            "languages": [
                {"language": lang.language, "percentage": round(lang.percentage, 1)}
                for lang in repo.languages
            ],
            "recent_good_first_issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "difficulty_estimate": i.difficulty_estimate,
                    "comment_count": i.comment_count,
                    "is_assigned": i.is_assigned,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                    "labels": i.labels if isinstance(i.labels, list) else [],
                    "html_url": i.html_url,
                }
                for i in gfis
            ],
            "has_contributing_guide": repo.has_contributing_guide,
            "has_code_of_conduct": repo.has_code_of_conduct,
            "has_readme": repo.has_readme,
            "has_issue_templates": repo.has_issue_templates,
            "has_pr_templates": repo.has_pr_templates,
            "synced_at": repo.synced_at.isoformat() if repo.synced_at else None,
        }

    return await cache.get_or_set(cache_key, settings.cache_ttl_repo_detail, _fetch)


async def get_repo_metrics_history(
    db: AsyncSession,
    cache: CacheService,
    repo_id: int,
) -> list[dict]:
    cache_key = f"repos:{repo_id}:history"

    async def _fetch():
        stmt = (
            select(RepoMetricsHistory)
            .where(RepoMetricsHistory.repo_id == repo_id)
            .order_by(RepoMetricsHistory.recorded_date.asc())
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "date": row.recorded_date.isoformat(),
                "activity_score": row.activity_score,
                "beginner_friendliness_score": row.beginner_friendliness_score,
                "stars": row.stars,
                "forks": row.forks,
                "good_first_issue_count": row.good_first_issue_count,
                "avg_pr_merge_hours": row.avg_pr_merge_hours,
            }
            for row in rows
        ]

    return await cache.get_or_set(cache_key, settings.cache_ttl_history, _fetch)
