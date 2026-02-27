
from __future__ import annotations

import math
from typing import Any

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.cache import CacheService
from app.models.issue import Issue
from app.models.repository import Repository
from app.schemas.issue import IssueQueryParams


async def get_issues(
    db: AsyncSession,
    cache: CacheService,
    params: IssueQueryParams,
) -> dict[str, Any]:
    cache_key = f"issues:list:{CacheService.hash_params(params.model_dump())}"

    async def _fetch():
        base = (
            select(Issue, Repository.full_name, Repository.primary_language)
            .join(Repository, Issue.repo_id == Repository.id)
            .where(Issue.state == "open", Issue.is_good_first_issue == True)  # noqa
            .where(Repository.is_active == True)  # noqa
        )

        if params.language:
            base = base.where(Repository.primary_language.ilike(params.language))
        if params.difficulty:
            base = base.where(Issue.difficulty_estimate == params.difficulty)
        if params.is_assigned is not None:
            base = base.where(Issue.is_assigned == params.is_assigned)
        if params.search:
            pattern = f"%{params.search}%"
            base = base.where(
                or_(Issue.title.ilike(pattern), Issue.body_preview.ilike(pattern))
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        sort_map = {
            "created_at": Issue.created_at,
            "comment_count": Issue.comment_count,
        }
        sort_col = sort_map.get(params.sort_by, Issue.created_at)
        if params.order == "asc":
            base = base.order_by(sort_col.asc().nulls_last())
        else:
            base = base.order_by(sort_col.desc().nulls_last())

        base = base.offset(params.offset).limit(params.per_page)
        result = await db.execute(base)
        rows = result.all()

        return {
            "data": [
                {
                    "id": issue.id,
                    "github_id": issue.github_id,
                    "repo_id": issue.repo_id,
                    "repo_full_name": full_name,
                    "repo_language": language,
                    "title": issue.title,
                    "body_preview": (issue.body_preview or "")[:200],
                    "html_url": issue.html_url,
                    "state": issue.state,
                    "labels": issue.labels if isinstance(issue.labels, list) else [],
                    "comment_count": issue.comment_count,
                    "difficulty_estimate": issue.difficulty_estimate,
                    "is_assigned": issue.is_assigned,
                    "is_good_first_issue": issue.is_good_first_issue,
                    "is_help_wanted": issue.is_help_wanted,
                    "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                }
                for issue, full_name, language in rows
            ],
            "pagination": {
                "page": params.page,
                "per_page": params.per_page,
                "total_items": total,
                "total_pages": math.ceil(total / params.per_page) if total else 0,
            },
        }

    return await cache.get_or_set(cache_key, settings.cache_ttl_issues, _fetch)
