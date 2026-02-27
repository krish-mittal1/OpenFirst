
from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.cache import CacheService
from app.core.dependencies import get_cache, get_db
from app.models.issue import Issue
from app.models.repository import Repository

router = APIRouter(tags=["Stats"])


@router.get("/stats")
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    cache_key = "stats:global"

    async def _fetch():
        repo_count = (
            await db.execute(
                select(func.count(Repository.id)).where(Repository.is_active == True)  # noqa
            )
        ).scalar() or 0

        issue_count = (
            await db.execute(
                select(func.count(Issue.id)).where(
                    Issue.is_good_first_issue == True, Issue.state == "open"  # noqa
                )
            )
        ).scalar() or 0

        language_count = (
            await db.execute(
                select(func.count(distinct(Repository.primary_language))).where(
                    Repository.primary_language.isnot(None),
                    Repository.is_active == True,  # noqa
                )
            )
        ).scalar() or 0

        avg_activity = (
            await db.execute(
                select(func.avg(Repository.activity_score)).where(
                    Repository.is_active == True  # noqa
                )
            )
        ).scalar()

        avg_bf = (
            await db.execute(
                select(func.avg(Repository.beginner_friendliness_score)).where(
                    Repository.is_active == True  # noqa
                )
            )
        ).scalar()

        total_stars = (
            await db.execute(
                select(func.sum(Repository.stars)).where(
                    Repository.is_active == True  # noqa
                )
            )
        ).scalar() or 0

        return {
            "total_repositories": repo_count,
            "total_open_issues": issue_count,
            "total_languages": language_count,
            "avg_activity_score": round(avg_activity, 1) if avg_activity else 0,
            "avg_beginner_friendliness_score": round(avg_bf, 1) if avg_bf else 0,
            "total_stars_tracked": total_stars,
        }

    return await cache.get_or_set(cache_key, settings.cache_ttl_stats, _fetch)


@router.get("/languages")
async def get_languages(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    cache_key = "languages:all"

    async def _fetch():
        stmt = (
            select(
                Repository.primary_language,
                func.count(Repository.id).label("repo_count"),
            )
            .where(
                Repository.primary_language.isnot(None),
                Repository.is_active == True,  # noqa
            )
            .group_by(Repository.primary_language)
            .order_by(func.count(Repository.id).desc())
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            {"language": lang, "repo_count": count}
            for lang, count in rows
        ]

    return await cache.get_or_set(cache_key, settings.cache_ttl_languages, _fetch)
