
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.notification import Notification
from app.models.subscription import UserSubscription

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("")
async def create_subscription(
    email: str = Query(..., description="User email"),
    language: str | None = Query(None, description="Language filter"),
    labels: str | None = Query(None, description="Comma-separated labels"),
    notify_on_new_match: bool = Query(True),
    notify_on_inactive: bool = Query(True),
    only_actively_merging: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    label_list = [l.strip() for l in labels.split(",")] if labels else []

    sub = UserSubscription(
        email=email,
        language=language,
        labels=label_list,
        notify_on_new_match=notify_on_new_match,
        notify_on_inactive=notify_on_inactive,
        only_actively_merging=only_actively_merging,
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)

    return {
        "id": sub.id,
        "email": sub.email,
        "language": sub.language,
        "labels": sub.labels,
        "notify_on_new_match": sub.notify_on_new_match,
        "notify_on_inactive": sub.notify_on_inactive,
        "only_actively_merging": sub.only_actively_merging,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
    }


@router.get("")
async def list_subscriptions(
    email: str = Query(..., description="User email"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.email == email, UserSubscription.is_active == True)  # noqa
        .order_by(UserSubscription.created_at.desc())
    )
    subs = result.scalars().all()
    return {
        "data": [
            {
                "id": s.id,
                "email": s.email,
                "language": s.language,
                "labels": s.labels,
                "notify_on_new_match": s.notify_on_new_match,
                "notify_on_inactive": s.notify_on_inactive,
                "only_actively_merging": s.only_actively_merging,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subs
        ],
        "total": len(subs),
    }


@router.delete("/{sub_id}")
async def delete_subscription(
    sub_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.id == sub_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub.is_active = False
    await db.commit()
    return {"status": "unsubscribed", "id": sub_id}


@router.get("/notifications")
async def get_notifications(
    email: str = Query(..., description="User email"),
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    import math

    sub_result = await db.execute(
        select(UserSubscription.id).where(UserSubscription.email == email)
    )
    sub_ids = [row[0] for row in sub_result]

    if not sub_ids:
        return {"data": [], "pagination": {"page": 1, "total_pages": 0, "total_items": 0}}

    count_stmt = select(func.count(Notification.id)).where(
        Notification.subscription_id.in_(sub_ids)
    )
    if unread_only:
        count_stmt = count_stmt.where(Notification.is_read == False)  # noqa
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Notification)
        .where(Notification.subscription_id.in_(sub_ids))
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa

    result = await db.execute(stmt)
    notifs = result.scalars().all()

    return {
        "data": [
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "repo_full_name": n.repo_full_name,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifs
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total,
            "total_pages": math.ceil(total / per_page) if total else 0,
        },
    }


@router.patch("/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id)
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    await db.commit()
    return {"status": "read", "id": notif_id}
