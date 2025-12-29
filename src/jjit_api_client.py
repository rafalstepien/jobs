import asyncio
import random
import typing

import aiohttp
import fake_useragent
from aiohttp.client_exceptions import ClientError, ServerDisconnectedError
from tenacity import AsyncRetrying, RetryError, retry_if_exception_type, stop_after_attempt, wait_exponential
from yarl import URL

from exceptions import APIError, RetryableAPIError
from models import ProgrammingLanguage, WebsiteErrorResponse, WebsiteOkResponse

RETRYABLE_ERROR_CODES = (408, 429, 502, 503, 504, 500)


class JJITAPIClient:
    def __init__(self):
        self._retry_scheme = AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=2, max=8),
            retry=retry_if_exception_type((RetryableAPIError, ClientError, ServerDisconnectedError)),
        )
        self._semaphore = asyncio.Semaphore(3)
        self._session_headers = {
            "User-Agent": fake_useragent.UserAgent().random,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "text/plain;charset=UTF-8",
            "Referer": "https://justjoin.it/",
        }

    async def fetch_multiple_urls(self, urls: list[URL]) -> typing.AsyncGenerator[WebsiteOkResponse]:
        async with aiohttp.ClientSession(headers=self._session_headers) as session:
            tasks = [asyncio.create_task(self._request_with_retry(session, url, random.uniform(1, 3))) for url in urls]
            async for t in asyncio.as_completed(tasks):
                result = await t
                if isinstance(result, WebsiteOkResponse):
                    yield result
                else:
                    print(f"There was error in response: {result}")

    async def fetch_base_board(self, language: ProgrammingLanguage, include_skills: list[str]) -> WebsiteOkResponse:
        url = URL.build(
            scheme="https",
            host="justjoin.it",
            path=f"/job-offers/all-locations/{language.lower()}",
            query=_get_query_string_from_criteria(include_skills),
        )
        r = await self._fetch_single_url(url)
        if isinstance(r, WebsiteErrorResponse):
            raise APIError("Fetching the board was unsuccessful")
        return r

    def build_url_for_individual_offer(self, offer_path: str) -> URL:
        return URL.build(scheme="https", host="justjoin.it", path=f"{offer_path}")

    async def _fetch_single_url(self, url: URL) -> WebsiteErrorResponse | WebsiteOkResponse:
        async with aiohttp.ClientSession(headers=self._session_headers) as session:
            return await self._request_with_retry(session, url)

    async def _request_with_retry(
        self, session: aiohttp.ClientSession, url: URL, sleep: float = 0
    ) -> WebsiteErrorResponse | WebsiteOkResponse:
        await asyncio.sleep(sleep)  # Simulate human behavior
        try:
            async for attempt in self._retry_scheme:
                with attempt:
                    async with self._semaphore:
                        async with session.get(url) as response:
                            if response.ok:
                                return WebsiteOkResponse(html=await response.text(), url=url)
                            else:
                                if response.status in RETRYABLE_ERROR_CODES:
                                    raise RetryableAPIError(message="", status=response.status)
                                else:
                                    return WebsiteErrorResponse(
                                        status=response.status,
                                        url=url,
                                        msg="Request failed and was not suitable for retry",
                                    )

        except RetryError as e:
            status = exc.status if (exc := e.last_attempt.exception()) else None  # type: ignore[attr-defined]
            return WebsiteErrorResponse(status=status, url=url, msg="Number of retries exceeded")

        return WebsiteErrorResponse(msg="Unexpected retry exhaustion", status=None, url=url)


def _get_query_string_from_criteria(include_skills: list[str]) -> str:
    skills_strings = []
    for skill in include_skills:
        if skill.islower():
            skill = skill.capitalize()
        skills_strings.append(f"skills={skill}")
    return "&".join(skills_strings)
