
from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _days_since(dt: datetime | None) -> float:
    if dt is None:
        return 999.0
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
    return max(delta.total_seconds() / 86400, 0)


def calculate_activity_score(
    last_commit_at: datetime | None = None,
    last_pushed_at: datetime | None = None,
    avg_pr_merge_hours: float | None = None,
    avg_issue_response_hours: float | None = None,
    merged_pr_count: int = 0,
    closed_pr_count: int = 0,
    open_pr_count: int = 0,
    contributor_count: int = 0,
    stars: int = 0,
    forks: int = 0,
    **_kwargs,
) -> float:
    score = 0.0

    days = _days_since(last_commit_at)
    if days < 1:
        score += 25
    elif days < 7:
        score += 20
    elif days < 30:
        score += 15
    elif days < 90:
        score += 8
    elif days < 180:
        score += 3

    if avg_pr_merge_hours is not None:
        if avg_pr_merge_hours < 24:
            score += 20
        elif avg_pr_merge_hours < 72:
            score += 15
        elif avg_pr_merge_hours < 168:
            score += 10
        elif avg_pr_merge_hours < 720:
            score += 5

    if avg_issue_response_hours is not None:
        if avg_issue_response_hours < 12:
            score += 15
        elif avg_issue_response_hours < 48:
            score += 12
        elif avg_issue_response_hours < 168:
            score += 7
        elif avg_issue_response_hours < 720:
            score += 3

    total_completed_prs = merged_pr_count + closed_pr_count
    if total_completed_prs > 0:
        merge_rate = merged_pr_count / total_completed_prs
        score += merge_rate * 15

    score += min(contributor_count / 100, 1.0) * 8
    if stars > 0:
        score += min(stars / 5000, 1.0) * 4
    if forks > 0:
        score += min(forks / 1000, 1.0) * 3

    push_days = _days_since(last_pushed_at)
    if push_days < 1:
        score += 10
    elif push_days < 7:
        score += 8
    elif push_days < 30:
        score += 5
    elif push_days < 90:
        score += 2

    return round(min(score, 100.0), 1)


def calculate_beginner_friendliness_score(
    good_first_issue_count: int = 0,
    has_contributing_guide: bool = False,
    has_code_of_conduct: bool = False,
    has_readme: bool = False,
    has_issue_templates: bool = False,
    has_pr_templates: bool = False,
    license_type: str | None = None,
    avg_issue_response_hours: float | None = None,
    avg_pr_merge_hours: float | None = None,
    stars: int = 0,
    contributor_count: int = 0,
    merged_pr_count: int = 0,
    **_kwargs,
) -> float:
    score = 0.0

    if good_first_issue_count >= 10:
        score += 25
    elif good_first_issue_count >= 5:
        score += 20
    elif good_first_issue_count >= 3:
        score += 15
    elif good_first_issue_count >= 1:
        score += 8

    if has_readme:
        score += 5
    if has_contributing_guide:
        score += 7
    if has_code_of_conduct:
        score += 3
    if has_issue_templates:
        score += 3
    if has_pr_templates:
        score += 2

    if avg_issue_response_hours is not None:
        if avg_issue_response_hours < 24:
            score += 10
        elif avg_issue_response_hours < 72:
            score += 7
        elif avg_issue_response_hours < 168:
            score += 4

    if avg_pr_merge_hours is not None:
        if avg_pr_merge_hours < 48:
            score += 10
        elif avg_pr_merge_hours < 168:
            score += 7
        elif avg_pr_merge_hours < 720:
            score += 3

    score += min(contributor_count / 200, 1.0) * 8
    if 100 <= stars <= 50000:
        score += 7
    elif stars > 50000:
        score += 4
    elif stars >= 50:
        score += 3

    friendly_licenses = {
        "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
        "ISC", "Unlicense", "0BSD",
    }
    if license_type in friendly_licenses:
        score += 10
    elif license_type:
        score += 4

    if merged_pr_count > 0:
        score += min(merged_pr_count / 500, 1.0) * 10

    return round(min(score, 100.0), 1)


def calculate_combined_score(
    activity_score: float,
    beginner_friendliness_score: float,
    activity_weight: float = 0.4,
    bf_weight: float = 0.6,
) -> float:
    return round(
        (activity_score * activity_weight)
        + (beginner_friendliness_score * bf_weight),
        1,
    )


def estimate_issue_difficulty(
    labels: list[str] | None = None,
    body: str | None = None,
    comment_count: int = 0,
) -> str:
    signals = {"easy": 0, "medium": 0, "hard": 0}

    label_set = {l.lower() for l in (labels or [])}

    easy_labels = {
        "good first issue", "beginner", "easy", "starter", "low-hanging-fruit",
        "first-timers-only", "up-for-grabs", "documentation", "typo", "docs",
    }
    medium_labels = {
        "enhancement", "feature", "improvement", "help wanted", "medium",
    }
    hard_labels = {
        "bug", "performance", "security", "breaking", "complex", "hard",
        "architecture", "refactor", "critical",
    }

    for label in label_set:
        if label in easy_labels:
            signals["easy"] += 2
        if label in medium_labels:
            signals["medium"] += 2
        if label in hard_labels:
            signals["hard"] += 2

    body_len = len(body or "")
    if body_len < 200:
        signals["easy"] += 1
    elif body_len < 800:
        signals["medium"] += 1
    else:
        signals["hard"] += 1

    if comment_count <= 2:
        signals["easy"] += 1
    elif comment_count <= 5:
        signals["medium"] += 1
    else:
        signals["hard"] += 1

    return max(signals, key=signals.get)  # type: ignore[arg-type]
