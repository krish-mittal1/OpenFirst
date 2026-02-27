
import asyncio
import logging
import time
from typing import Any

import httpx

from app.config import settings
from app.core.exceptions import GitHubAPIError, RateLimitExceededError

logger = logging.getLogger(__name__)


class GitHubClient:

    def __init__(self):
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_pat:
            self._headers["Authorization"] = f"Bearer {settings.github_pat}"

        self._client: httpx.AsyncClient | None = None
        self._rate_remaining: int = 5000
        self._rate_reset: float = 0

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.github_api_base,
                headers=self._headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _update_rate_limit(self, headers: httpx.Headers):
        remaining = headers.get("x-ratelimit-remaining")
        reset = headers.get("x-ratelimit-reset")
        if remaining is not None:
            self._rate_remaining = int(remaining)
        if reset is not None:
            self._rate_reset = float(reset)
        if self._rate_remaining < 100:
            logger.warning("GitHub rate limit low: %d remaining", self._rate_remaining)

    async def _wait_for_rate_limit(self):
        if self._rate_remaining <= 1:
            wait_seconds = max(self._rate_reset - time.time(), 1)
            if wait_seconds > 0:
                logger.warning("Rate limited. Sleeping %.0f seconds", wait_seconds)
                await asyncio.sleep(min(wait_seconds, 60))

    async def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        retries: int | None = None,
    ) -> httpx.Response:
        retries = retries or settings.github_max_retries
        client = await self._get_client()

        for attempt in range(retries + 1):
            await self._wait_for_rate_limit()

            try:
                response = await client.request(method, url, params=params)
                self._update_rate_limit(response.headers)

                if response.status_code == 200:
                    return response
                elif response.status_code == 304:
                    return response
                elif response.status_code == 403:
                    if self._rate_remaining <= 0:
                        raise RateLimitExceededError()
                    raise GitHubAPIError(f"Forbidden: {response.text}", 403)
                elif response.status_code == 404:
                    raise GitHubAPIError(f"Not found: {url}", 404)
                elif response.status_code >= 500:
                    if attempt < retries:
                        delay = settings.github_retry_delay * (2 ** attempt)
                        logger.warning(
                            "GitHub 5xx (attempt %d/%d), retrying in %.1fs",
                            attempt + 1, retries, delay,
                        )
                        await asyncio.sleep(delay)
                        continue
                    raise GitHubAPIError(f"Server error: {response.status_code}")
                else:
                    raise GitHubAPIError(
                        f"Unexpected status {response.status_code}: {response.text}",
                        response.status_code,
                    )
            except httpx.RequestError as e:
                if attempt < retries:
                    delay = settings.github_retry_delay * (2 ** attempt)
                    logger.warning("Request error (attempt %d/%d): %s", attempt + 1, retries, e)
                    await asyncio.sleep(delay)
                    continue
                raise GitHubAPIError(f"Request failed: {e}")

        raise GitHubAPIError("Max retries exceeded")

    async def get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        response = await self.request("GET", url, params=params)
        if response.status_code == 304:
            return None
        return response.json()

    async def get_paginated(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        max_pages: int = 5,
    ) -> list[Any]:
        params = dict(params or {})
        params.setdefault("per_page", 100)

        all_items: list[Any] = []
        for page in range(1, max_pages + 1):
            params["page"] = page
            response = await self.request("GET", url, params=params)
            items = response.json()
            if not items:
                break
            all_items.extend(items)

            link_header = response.headers.get("link", "")
            if 'rel="next"' not in link_header:
                break

        return all_items


    async def get_repo(self, owner: str, repo: str) -> dict:
        return await self.get(f"/repos/{owner}/{repo}")

    async def get_repo_languages(self, owner: str, repo: str) -> dict:
        return await self.get(f"/repos/{owner}/{repo}/languages")

    async def get_repo_issues(
        self,
        owner: str,
        repo: str,
        labels: str = "good first issue",
        state: str = "open",
        max_pages: int = 3,
    ) -> list[dict]:
        return await self.get_paginated(
            f"/repos/{owner}/{repo}/issues",
            params={"labels": labels, "state": state, "per_page": 100},
            max_pages=max_pages,
        )

    async def get_repo_pulls(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        max_pages: int = 3,
    ) -> list[dict]:
        return await self.get_paginated(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "sort": "updated", "per_page": 100},
            max_pages=max_pages,
        )

    async def get_contributor_count(self, owner: str, repo: str) -> int:
        try:
            response = await self.request(
                "GET",
                f"/repos/{owner}/{repo}/contributors",
                params={"per_page": 1, "anon": "true"},
            )
            link = response.headers.get("link", "")
            if 'rel="last"' in link:
                import re
                match = re.search(r'page=(\d+)>; rel="last"', link)
                if match:
                    return int(match.group(1))
            return len(response.json())
        except Exception:
            return 0

    async def get_community_profile(self, owner: str, repo: str) -> dict:
        try:
            return await self.get(f"/repos/{owner}/{repo}/community/profile")
        except GitHubAPIError:
            return {}

    async def search_repositories(
        self,
        query: str,
        sort: str = "updated",
        order: str = "desc",
        per_page: int = 100,
        page: int = 1,
    ) -> dict:
        return await self.get(
            "/search/repositories",
            params={
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": per_page,
                "page": page,
            },
        )

    @property
    def rate_remaining(self) -> int:
        return self._rate_remaining


github_client = GitHubClient()
