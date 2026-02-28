
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.issue import Issue
from app.models.language import RepoLanguage
from app.models.metrics_history import RepoMetricsHistory
from app.models.repository import Repository
from app.services.github_client import github_client
from app.services.scoring_engine import (
    calculate_activity_score,
    calculate_beginner_friendliness_score,
    calculate_combined_score,
    estimate_issue_difficulty,
)

logger = logging.getLogger(__name__)

POPULAR_QUERIES = [
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:Python",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:JavaScript",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:TypeScript",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:Java",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:Go",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:Rust",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:C++",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:Ruby",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:PHP",
    "good-first-issues:>3 stars:>500 pushed:>{recent_date} archived:false language:C#",
]

BEGINNER_QUERIES = [
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:Python",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:JavaScript",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:TypeScript",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:Java",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:Go",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:Rust",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:C++",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:Ruby",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:PHP",
    "good-first-issues:>1 stars:10..500 pushed:>{recent_date} archived:false language:C#",
]

DISCOVERY_QUERIES = POPULAR_QUERIES + BEGINNER_QUERIES


def _parse_datetime(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


async def discover_repositories(max_pages_per_query: int = 3) -> list[dict]:
    from datetime import timedelta

    recent_date = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%d")
    all_repos: dict[str, dict] = {}

    for query_template in DISCOVERY_QUERIES:
        query = query_template.format(recent_date=recent_date)
        logger.info("Searching: %s", query)

        for page in range(1, max_pages_per_query + 1):
            try:
                result = await github_client.search_repositories(
                    query=query, sort="updated", order="desc", per_page=100, page=page
                )
                items = result.get("items", [])
                if not items:
                    break

                for item in items:
                    full_name = item["full_name"]
                    if full_name not in all_repos:
                        all_repos[full_name] = item

                logger.info(
                    "  Page %d: %d repos (total unique: %d)",
                    page, len(items), len(all_repos),
                )

                if len(items) < 100:
                    break
            except Exception as e:
                logger.error("Search error (page %d): %s", page, e)
                break

    logger.info("Discovery complete: %d unique repos found", len(all_repos))
    return list(all_repos.values())


async def sync_single_repo(session: AsyncSession, repo_data: dict) -> Repository | None:
    full_name = repo_data["full_name"]
    owner, name = full_name.split("/", 1)

    try:
        logger.info("Syncing %s ...", full_name)

        contributor_count = await github_client.get_contributor_count(owner, name)

        languages_data = await github_client.get_repo_languages(owner, name)

        gfi_data = await github_client.get_repo_issues(
            owner, name, labels="good first issue", state="open", max_pages=3
        )

        pr_data = await github_client.get_repo_pulls(
            owner, name, state="all", max_pages=2
        )

        community = await github_client.get_community_profile(owner, name)

        merged_prs = [p for p in pr_data if p.get("merged_at")]
        closed_prs = [p for p in pr_data if p.get("state") == "closed" and not p.get("merged_at")]
        open_prs = [p for p in pr_data if p.get("state") == "open"]

        avg_pr_merge_hours = None
        if merged_prs:
            merge_times = []
            for pr in merged_prs:
                created = _parse_datetime(pr["created_at"])
                merged = _parse_datetime(pr["merged_at"])
                if created and merged:
                    hours = (merged - created).total_seconds() / 3600
                    merge_times.append(hours)
            if merge_times:
                avg_pr_merge_hours = sum(merge_times) / len(merge_times)

        avg_issue_response_hours = None
        if gfi_data:
            commented = [i for i in gfi_data if i.get("comments", 0) > 0]
            if commented:
                response_times = []
                for issue in commented[:20]:
                    created = _parse_datetime(issue["created_at"])
                    updated = _parse_datetime(issue["updated_at"])
                    if created and updated and updated > created:
                        hours = (updated - created).total_seconds() / 3600
                        response_times.append(min(hours, 720))
                if response_times:
                    avg_issue_response_hours = sum(response_times) / len(response_times)

        total_bytes = sum(languages_data.values()) if languages_data else 0
        language_breakdown = []
        if total_bytes > 0:
            for lang, bytes_count in languages_data.items():
                language_breakdown.append({
                    "language": lang,
                    "bytes_count": bytes_count,
                    "percentage": round((bytes_count / total_bytes) * 100, 1),
                })

        files = community.get("files", {}) if community else {}
        has_contributing = files.get("contributing") is not None
        has_coc = files.get("code_of_conduct") is not None
        has_readme = files.get("readme") is not None
        has_issue_template = files.get("issue_template") is not None
        has_pr_template = files.get("pull_request_template") is not None

        license_info = repo_data.get("license")
        license_type = license_info.get("spdx_id") if license_info else None

        score_inputs = {
            "last_commit_at": _parse_datetime(repo_data.get("pushed_at")),
            "last_pushed_at": _parse_datetime(repo_data.get("pushed_at")),
            "avg_pr_merge_hours": avg_pr_merge_hours,
            "avg_issue_response_hours": avg_issue_response_hours,
            "merged_pr_count": len(merged_prs),
            "closed_pr_count": len(closed_prs),
            "open_pr_count": len(open_prs),
            "contributor_count": contributor_count,
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "good_first_issue_count": len(gfi_data),
            "has_contributing_guide": has_contributing,
            "has_code_of_conduct": has_coc,
            "has_readme": has_readme,
            "has_issue_templates": has_issue_template,
            "has_pr_templates": has_pr_template,
            "license_type": license_type,
        }

        activity = calculate_activity_score(**score_inputs)
        bf = calculate_beginner_friendliness_score(**score_inputs)
        combined = calculate_combined_score(activity, bf)

        total_completed_prs = len(merged_prs) + len(closed_prs)
        pr_merge_rate = len(merged_prs) / total_completed_prs if total_completed_prs > 0 else 0.0

        last_merged_pr_at = None
        if merged_prs:
            merge_dates = [_parse_datetime(p["merged_at"]) for p in merged_prs if p.get("merged_at")]
            if merge_dates:
                last_merged_pr_at = max(d for d in merge_dates if d is not None)

        from datetime import timedelta
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_merged_30d = sum(
            1 for p in merged_prs
            if _parse_datetime(p.get("merged_at"))
            and _parse_datetime(p["merged_at"]) > thirty_days_ago
        )

        commit_within_30d = _parse_datetime(repo_data.get("pushed_at")) and \
            _parse_datetime(repo_data["pushed_at"]) > thirty_days_ago
        merged_within_30d = last_merged_pr_at and last_merged_pr_at > thirty_days_ago
        is_actively_merging = all([
            commit_within_30d,
            merged_within_30d,
            pr_merge_rate > 0.5,
            contributor_count > 5,
            not repo_data.get("archived", False),
        ])

        repo_values = {
            "github_id": str(repo_data["id"]),
            "full_name": full_name,
            "owner": owner,
            "name": name,
            "description": (repo_data.get("description") or "")[:2000],
            "primary_language": repo_data.get("language"),
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "open_issues_count": repo_data.get("open_issues_count", 0),
            "watchers": repo_data.get("watchers_count", 0),
            "license": license_type,
            "created_at": _parse_datetime(repo_data.get("created_at")),
            "last_pushed_at": _parse_datetime(repo_data.get("pushed_at")),
            "last_commit_at": _parse_datetime(repo_data.get("pushed_at")),
            "activity_score": activity,
            "beginner_friendliness_score": bf,
            "combined_score": combined,
            "good_first_issue_count": len(gfi_data),
            "contributor_count": contributor_count,
            "avg_pr_merge_hours": avg_pr_merge_hours,
            "avg_issue_response_hours": avg_issue_response_hours,
            "open_pr_count": len(open_prs),
            "closed_pr_count": len(closed_prs),
            "merged_pr_count": len(merged_prs),
            "has_contributing_guide": has_contributing,
            "has_code_of_conduct": has_coc,
            "has_readme": has_readme,
            "has_issue_templates": has_issue_template,
            "has_pr_templates": has_pr_template,
            "last_merged_pr_at": last_merged_pr_at,
            "pr_merge_rate": round(pr_merge_rate, 3),
            "recent_merged_pr_count_30d": recent_merged_30d,
            "is_actively_merging": is_actively_merging,
            "topics": repo_data.get("topics", []),
            "synced_at": datetime.now(timezone.utc),
            "is_active": True,
        }

        stmt = pg_insert(Repository).values(**repo_values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["github_id"],
            set_={k: v for k, v in repo_values.items() if k != "github_id"},
        )
        await session.execute(stmt)
        await session.flush()

        result = await session.execute(
            select(Repository).where(Repository.github_id == str(repo_data["id"]))
        )
        repo = result.scalar_one()

        for lang_info in language_breakdown:
            lang_stmt = pg_insert(RepoLanguage).values(
                repo_id=repo.id,
                language=lang_info["language"],
                bytes_count=lang_info["bytes_count"],
                percentage=lang_info["percentage"],
            )
            lang_stmt = lang_stmt.on_conflict_do_update(
                constraint="uq_repo_language",
                set_={
                    "bytes_count": lang_info["bytes_count"],
                    "percentage": lang_info["percentage"],
                },
            )
            await session.execute(lang_stmt)

        for issue_data in gfi_data:
            labels = [l["name"] for l in issue_data.get("labels", [])]
            difficulty = estimate_issue_difficulty(
                labels=labels,
                body=issue_data.get("body"),
                comment_count=issue_data.get("comments", 0),
            )
            assignee = issue_data.get("assignee")

            issue_values = {
                "github_id": str(issue_data["id"]),
                "repo_id": repo.id,
                "title": issue_data["title"][:500],
                "body_preview": (issue_data.get("body") or "")[:500],
                "html_url": issue_data.get("html_url"),
                "state": issue_data.get("state", "open"),
                "labels": labels,
                "comment_count": issue_data.get("comments", 0),
                "difficulty_estimate": difficulty,
                "assignee_login": assignee["login"] if assignee else None,
                "is_assigned": assignee is not None,
                "is_good_first_issue": True,
                "is_help_wanted": any("help wanted" in l.lower() for l in labels),
                "created_at": _parse_datetime(issue_data.get("created_at")),
                "updated_at": _parse_datetime(issue_data.get("updated_at")),
                "closed_at": _parse_datetime(issue_data.get("closed_at")),
                "synced_at": datetime.now(timezone.utc),
            }

            issue_stmt = pg_insert(Issue).values(**issue_values)
            issue_stmt = issue_stmt.on_conflict_do_update(
                index_elements=["github_id"],
                set_={k: v for k, v in issue_values.items() if k != "github_id"},
            )
            await session.execute(issue_stmt)

        from datetime import date as date_type
        history_stmt = pg_insert(RepoMetricsHistory).values(
            repo_id=repo.id,
            activity_score=activity,
            beginner_friendliness_score=bf,
            stars=repo.stars,
            forks=repo.forks,
            good_first_issue_count=len(gfi_data),
            avg_pr_merge_hours=avg_pr_merge_hours,
            recorded_date=date_type.today(),
        )
        history_stmt = history_stmt.on_conflict_do_update(
            constraint="uq_repo_metrics_date",
            set_={
                "activity_score": activity,
                "beginner_friendliness_score": bf,
                "stars": repo.stars,
                "forks": repo.forks,
                "good_first_issue_count": len(gfi_data),
                "avg_pr_merge_hours": avg_pr_merge_hours,
            },
        )
        await session.execute(history_stmt)

        await session.commit()
        logger.info(
            "✓ %s | Activity: %.1f | BF: %.1f | Combined: %.1f | GFIs: %d",
            full_name, activity, bf, combined, len(gfi_data),
        )
        return repo

    except Exception as e:
        logger.error("✗ Failed to sync %s: %s", full_name, e)
        await session.rollback()
        return None


async def run_full_sync(max_repos: int = 200):
    logger.info("═══ Starting full sync (max %d repos) ═══", max_repos)

    candidates = await discover_repositories(max_pages_per_query=2)
    logger.info("Discovered %d candidate repos", len(candidates))

    candidates.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
    candidates = candidates[:max_repos]

    success = 0
    for repo_data in candidates:
        async with async_session_factory() as session:
            result = await sync_single_repo(session, repo_data)
            if result:
                success += 1

        if github_client.rate_remaining < 200:
            import asyncio
            logger.warning("Rate limit low (%d), pausing 30s", github_client.rate_remaining)
            await asyncio.sleep(30)

    await mark_inactive_repos()

    try:
        from app.services.notification_service import check_subscriptions
        await check_subscriptions()
    except Exception as e:
        logger.error("Notification check failed: %s", e)

    logger.info("═══ Sync complete: %d/%d repos synced ═══", success, len(candidates))


async def mark_inactive_repos():
    from datetime import timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(days=60)

    async with async_session_factory() as session:
        stmt = (
            select(Repository)
            .where(
                Repository.is_active == True,  # noqa
                Repository.last_commit_at < cutoff,
            )
        )
        result = await session.execute(stmt)
        stale_repos = result.scalars().all()

        for repo in stale_repos:
            repo.is_active = False
            repo.is_actively_merging = False
            logger.info("Marked %s as inactive (last commit: %s)", repo.full_name, repo.last_commit_at)

        if stale_repos:
            await session.commit()
            logger.info("Marked %d repos as inactive", len(stale_repos))
