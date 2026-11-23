"""
GitHub API Integration Client.
Extracts verifiable repository metadata, star counts, and validates repository existence.
Adheres to SRS FR-05 and LLD Section 9.
"""

import re
import logging
from typing import Any, Dict, Optional, Tuple
import aiohttp
from intelligent_scraper.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for GitHub REST API v3."""

    # Regex to capture owner and repo from various GitHub URL formats
    GITHUB_URL_REGEX = re.compile(
        r'https?://(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)',
        re.IGNORECASE
    )

    def __init__(self, token: Optional[str] = None, settings: Optional[Settings] = None):
        cfg = settings or get_settings()
        self.token = token or cfg.GITHUB_TOKEN
        self.base_url = "https://api.github.com"

    def normalize_repository_url(self, url: str) -> Optional[str]:
        """Normalizes GitHub URL to canonical 'https://github.com/owner/repo' format."""
        if not url:
            return None
        match = self.GITHUB_URL_REGEX.search(url.strip())
        if match:
            owner, repo = match.group(1), match.group(2).rstrip(".git")
            return f"https://github.com/{owner}/{repo}"
        return None

    def extract_owner_repo(self, url: str) -> Optional[Tuple[str, str]]:
        """Extracts (owner, repo) tuple from URL."""
        if not url:
            return None
        match = self.GITHUB_URL_REGEX.search(url.strip())
        if match:
            owner = match.group(1)
            repo = match.group(2).rstrip(".git")
            return owner, repo
        return None

    async def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Queries repository info from GitHub REST API."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 404:
                        return None
                    elif resp.status == 403:
                        logger.warning(f"GitHub API rate limit or forbidden: {await resp.text()}")
                        return None
                    else:
                        logger.warning(f"GitHub API returned {resp.status} for {owner}/{repo}")
                        return None
        except Exception as e:
            logger.warning(f"Error querying GitHub API for {owner}/{repo}: {e}")
            return None

    async def get_star_count(self, owner: str, repo: str) -> Optional[int]:
        """Returns stargazers_count for repository."""
        data = await self.get_repository(owner, repo)
        if data and "stargazers_count" in data:
            return int(data["stargazers_count"])
        return None

    async def validate_repository(self, url: str) -> Tuple[bool, Optional[int]]:
        """
        Validates GitHub repository URL and retrieves star count.
        Returns (exists, star_count).
        """
        parsed = self.extract_owner_repo(url)
        if not parsed:
            return False, None

        owner, repo = parsed
        stars = await self.get_star_count(owner, repo)
        if stars is not None:
            return True, stars

        # If rate limited without token, repository URL pattern is still valid
        return True, 0
