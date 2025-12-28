import asyncio
import random
import typing
from dataclasses import dataclass

import aiohttp
import fake_useragent
from aiohttp.client_exceptions import ClientError, ServerDisconnectedError
from tenacity import AsyncRetrying, RetryError, retry_if_exception_type, stop_after_attempt, wait_exponential
from yarl import URL

from exceptions import RetryableAPIError
from models import WebsiteResponse

ua = fake_useragent.UserAgent()


def log_retry(retry_state):
    print(f"Retrying {retry_state.fn}: attempt {retry_state.attempt_number}")


session_args: dict[str, dict] = {
    "headers": {
        "User-Agent": ua.random,
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "text/plain;charset=UTF-8",
        "Referer": "https://justjoin.it/",
    }
}

RETRYABLE_ERROR_CODES = (408, 429, 502, 503, 504, 500)


@dataclass(frozen=True, slots=True)
class ErrorResponse:
    url: URL
    msg: str
    status: int | None = None


class JJITAPIClient:
    def __init__(self):
        self._retry_scheme = AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=2, max=8),
            retry=retry_if_exception_type((RetryableAPIError, ClientError, ServerDisconnectedError)),
            after=log_retry,
        )
        self._semaphore = asyncio.Semaphore(3)
        self._session = aiohttp.ClientSession(headers=session_args["headers"])

    async def fetch_multiple_urls(self, urls: list[URL]) -> typing.AsyncGenerator[ErrorResponse | WebsiteResponse]:
        async with self._session as session:
            tasks = [asyncio.create_task(self._request_with_retry(session, url, random.uniform(1, 3))) for url in urls]
            async for t in asyncio.as_completed(tasks):
                yield await t

    async def fetch_single_url(self, url: URL) -> ErrorResponse | WebsiteResponse:
        async with self._session as session:
            return await self._request_with_retry(session, url)

    async def _request_with_retry(
        self, session: aiohttp.ClientSession, url: URL, sleep: float = 0
    ) -> ErrorResponse | WebsiteResponse:
        await asyncio.sleep(sleep)  # Simulate human behavior
        try:
            async for attempt in self._retry_scheme:
                with attempt:
                    async with self._semaphore:
                        async with session.get(url) as response:
                            if response.ok:
                                return WebsiteResponse(html=await response.text(), url=url)
                            else:
                                if response.status in RETRYABLE_ERROR_CODES:
                                    raise RetryableAPIError(message="", status=response.status)
                                else:
                                    return ErrorResponse(
                                        status=response.status,
                                        url=url,
                                        msg="Request failed and was not suitable for retry",
                                    )

        except RetryError as e:
            status = exc.status if (exc := e.last_attempt.exception()) else None
            return ErrorResponse(status=status, url=url, msg="Number of retries exceeded")

        return ErrorResponse(msg="Unexpected retry exhaustion", status=None, url=url)


# async def main():
#     c = JJITAPIClient()
#     urls = [
#         "http://localhost:80/status/429",  # R
#         "http://localhost:80/status/429",  # R
#         "http://localhost:80/status/500",  # R
#         "http://localhost:80/status/200",  # S
#         "http://localhost:80/status/200",  # S
#         "http://localhost:80/status/200",  # S
#         "http://localhost:80/status/408",  # R
#         "http://localhost:80/status/502",  # R
#         "http://localhost:80/status/500",  # R
#         "http://localhost:80/status/200",  # S
#         "http://localhost:80/status/200",  # S
#         "http://localhost:80/status/500",  # R
#         "http://localhost:80/status/200",  # S
#     ]
#     async for r in c.fetch_multiple_urls(urls):
#         print(r)


# if __name__ == "__main__":
#     result = asyncio.run(main(), debug=True)
