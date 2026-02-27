
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.notification import Notification
from app.models.repository import Repository
from app.models.subscription import UserSubscription

logger = logging.getLogger(__name__)


async def check_subscriptions():
    async with async_session_factory() as session:
        subs_result = await session.execute(
            select(UserSubscription).where(UserSubscription.is_active == True)  # noqa
        )
        subscriptions = subs_result.scalars().all()

        if not subscriptions:
            logger.debug("No active subscriptions to check")
            return

        for sub in subscriptions:
            try:
                await _process_subscription(session, sub)
            except Exception as e:
                logger.error("Error processing subscription %d: %s", sub.id, e)

        await session.commit()
        logger.info("Processed %d subscriptions", len(subscriptions))


async def _process_subscription(session: AsyncSession, sub: UserSubscription):

    cutoff = datetime.now(timezone.utc) - timedelta(hours=2)

    stmt = select(Repository).where(
        Repository.synced_at >= cutoff,
        Repository.is_active == True,  # noqa
    )

    if sub.language:
        stmt = stmt.where(Repository.primary_language.ilike(sub.language))

    if sub.only_actively_merging:
        stmt = stmt.where(Repository.is_actively_merging == True)  # noqa

    result = await session.execute(stmt)
    matching_repos = result.scalars().all()

    for repo in matching_repos:
        if sub.labels:
            repo_labels = set()
            from app.models.issue import Issue
            issues_result = await session.execute(
                select(Issue.labels).where(
                    Issue.repo_id == repo.id,
                    Issue.state == "open",
                )
            )
            for row in issues_result:
                if row[0] and isinstance(row[0], list):
                    repo_labels.update(l.lower() for l in row[0])

            sub_labels = {l.lower() for l in sub.labels}
            if not sub_labels.intersection(repo_labels):
                continue

        existing = await session.execute(
            select(Notification).where(
                Notification.subscription_id == sub.id,
                Notification.repo_id == repo.id,
                Notification.type == "new_match",
            )
        )
        if existing.scalar_one_or_none():
            continue

        if sub.notify_on_new_match:
            notif = Notification(
                subscription_id=sub.id,
                repo_id=repo.id,
                type="new_match",
                repo_full_name=repo.full_name,
                message=f"New match: {repo.full_name} ({repo.primary_language}) "
                        f"— Activity: {repo.activity_score:.0f}, "
                        f"BF: {repo.beginner_friendliness_score:.0f}, "
                        f"PR merge rate: {repo.pr_merge_rate:.0%}",
            )
            session.add(notif)
            logger.info("Created new_match notification for %s → %s", sub.email, repo.full_name)

    if sub.notify_on_inactive:
        inactive_result = await session.execute(
            select(Notification).where(
                Notification.subscription_id == sub.id,
                Notification.type == "new_match",
            )
        )
        prev_notifs = inactive_result.scalars().all()

        for prev in prev_notifs:
            if prev.repo_id is None:
                continue
            repo_result = await session.execute(
                select(Repository).where(Repository.id == prev.repo_id)
            )
            repo = repo_result.scalar_one_or_none()
            if repo and not repo.is_active:
                existing_inactive = await session.execute(
                    select(Notification).where(
                        Notification.subscription_id == sub.id,
                        Notification.repo_id == repo.id,
                        Notification.type == "went_inactive",
                    )
                )
                if not existing_inactive.scalar_one_or_none():
                    notif = Notification(
                        subscription_id=sub.id,
                        repo_id=repo.id,
                        type="went_inactive",
                        repo_full_name=repo.full_name,
                        message=f"⚠️ {repo.full_name} appears to be inactive "
                                f"(no commits since {repo.last_commit_at.strftime('%Y-%m-%d') if repo.last_commit_at else 'unknown'})",
                    )
                    session.add(notif)
                    logger.info("Created went_inactive notification for %s → %s", sub.email, repo.full_name)
