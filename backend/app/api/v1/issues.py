
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.dependencies import get_cache, get_db
from app.schemas.issue import IssueQueryParams
from app.services import issue_service

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.get("")
async def list_issues(
    language: str | None = Query(None, description="Filter by repo language"),
    difficulty: str | None = Query(None, pattern="^(easy|medium|hard)$"),
    is_assigned: bool | None = Query(None, description="Filter by assignment status"),
    search: str | None = Query(None, description="Search titles"),
    sort_by: str = Query("created_at", pattern="^(created_at|comment_count)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    params = IssueQueryParams(
        language=language,
        difficulty=difficulty,
        is_assigned=is_assigned,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        per_page=per_page,
    )
    return await issue_service.get_issues(db, cache, params)
