from __future__ import annotations

import asyncio
import logging
import time
from collections import deque

import httpx

from ..config import config

logger = logging.getLogger("sfx-mcp")


class FreeSoundAPI:
    """HTTP client for the FreeSound API v2.

    Handles rate limiting (~18 req/min to stay under the 20/min free tier cap),
    pagination, and auth via Bearer token.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None
        self._request_times: deque[float] = deque()
        self._semaphore = asyncio.Semaphore(3)

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=config.API_BASE_URL,
                timeout=30.0,
                headers={"Authorization": f"Token {self.api_key}"},
            )
        return self._client

    async def _rate_limit(self) -> None:
        now = time.monotonic()
        while self._request_times and now - self._request_times[0] > 60:
            self._request_times.popleft()
        if len(self._request_times) >= 18:
            sleep_for = 60 - (now - self._request_times[0])
            if sleep_for > 0:
                logger.debug("Rate limit: sleeping %.1fs", sleep_for)
                await asyncio.sleep(sleep_for)
        self._request_times.append(time.monotonic())

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        async with self._semaphore:
            await self._rate_limit()
            try:
                response = await self.client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                detail = e.response.text[:500]
                if status == 429:
                    logger.warning("FreeSound 429 (rate limited): %s", detail)
                    retry_after = int(e.response.headers.get("Retry-After", "60"))
                    await asyncio.sleep(retry_after)
                    return await self._request(method, path, **kwargs)
                if status == 401:
                    raise RuntimeError(
                        "FreeSound API key is invalid or missing. "
                        "Set FREESOUND_API_KEY in .env or environment."
                    ) from e
                raise RuntimeError(
                    f"FreeSound API error {status}: {detail}"
                ) from e
            except httpx.TimeoutException as e:
                raise RuntimeError(
                    "FreeSound API request timed out. Check network connectivity."
                ) from e

    async def search(
        self,
        query: str,
        duration_max: int = 30,
        tags: list[str] | None = None,
        page: int = 1,
        page_size: int = 15,
    ) -> dict:
        """Search CC0 sounds on FreeSound.

        Returns paginated results with sound metadata.
        """
        params = {
            "query": query,
            "filter": f"license:\"Creative Commons 0\" duration:[0 TO {duration_max}]",
            "page": page,
            "page_size": min(page_size, 50),
            "fields": "id,name,description,duration,samplerate,tags,previews,url,download",
        }
        return await self._request("GET", "/search/text/", params=params)

    async def get_sound_detail(self, sound_id: int) -> dict:
        """Get detailed metadata for a specific sound."""
        return await self._request(
            "GET",
            f"/sounds/{sound_id}/",
            params={
                "fields": "id,name,description,duration,samplerate,tags,previews,url,download,type"
            },
        )

    async def get_download_url(self, sound_id: int) -> str:
        """Get the download URL for a sound's original file.

        Returns the redirect URL for downloading.
        """
        data = await self._request("GET", f"/sounds/{sound_id}/download/")
        return data.get("download_url") or data.get("url", "")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
