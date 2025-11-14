"""XKCD API Extractor - Fetches comic data from xkcd.com API."""

import logging
from typing import Generator, Optional

import requests
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class XKCDComic(BaseModel):
    """XKCD Comic data model."""

    num: int = Field(..., description="Comic number (ID)")
    title: str = Field(..., description="Comic title")
    safe_title: str = Field(..., description="Title without special characters")
    alt: str = Field(..., description="Alternative text for the comic image")
    img: str = Field(..., description="URL to the comic image")
    transcript: str = Field(default="", description="Comic text transcript")
    year: str = Field(..., description="Publication year")
    month: str = Field(..., description="Publication month")
    day: str = Field(..., description="Publication day")
    link: str = Field(default="", description="Optional related link")
    news: str = Field(default="", description="Optional news/announcement text")


class XKCDExtractor:
    """Extract comic data from XKCD API."""

    def __init__(self, base_url: str = "https://xkcd.com", timeout: int = 30):
        """Initialize XKCD extractor."""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "XKCD-Ingestion"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
        reraise=True,
    )
    def fetch_current_comic(self) -> Optional[XKCDComic]:
        """Fetch the current/latest comic."""
        url = f"{self.base_url}/info.0.json"
        logger.info(f"Fetching current comic from {url}")

        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 404:
            logger.warning(f"Comic not found: {url}")
            return None
        response.raise_for_status()
        data = response.json()
        comic = XKCDComic(**data)
        logger.info(f"Successfully fetched comic #{comic.num}: {comic.title}")
        return comic

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
        reraise=True,
    )
    def fetch_comic_by_id(self, comic_id: int) -> Optional[XKCDComic]:
        """Fetch a specific comic by ID."""
        url = f"{self.base_url}/{comic_id}/info.0.json"
        logger.info(f"Fetching comic #{comic_id} from {url}")

        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 404:
            logger.warning(f"Comic #{comic_id} not found")
            return None
        response.raise_for_status()
        data = response.json()
        comic = XKCDComic(**data)
        logger.info(f"Successfully fetched comic #{comic.num}: {comic.title}")
        return comic

    def fetch_comic_range(
        self, start_id: int, end_id: int, skip_missing: bool = True
    ) -> Generator[XKCDComic, None, None]:
        """Fetch a range of comics."""
        logger.info(f"Fetching comics from #{start_id} to #{end_id}")

        for comic_id in range(start_id, end_id + 1):
            try:
                comic = self.fetch_comic_by_id(comic_id)
                if comic is not None:
                    yield comic
                elif not skip_missing:
                    raise ValueError(f"Comic #{comic_id} not found")
            except requests.RequestException as e:
                logger.error(f"Failed to fetch comic #{comic_id}: {e}")
                if not skip_missing:
                    raise

    def fetch_missing_comics(self, existing_ids: set[int]) -> Generator[XKCDComic, None, None]:
        """Fetch comics that are missing from the existing set."""
        # Get current comic to determine max ID
        current = self.fetch_current_comic()
        if current is None:
            logger.warning("Could not fetch current comic, cannot determine missing comics")
            return

        max_id = current.num
        logger.info(f"Checking for missing comics up to #{max_id}")

        for comic_id in range(1, max_id + 1):
            if comic_id not in existing_ids:
                try:
                    comic = self.fetch_comic_by_id(comic_id)
                    if comic is not None:
                        yield comic
                except requests.RequestException as e:
                    logger.error(f"Failed to fetch missing comic #{comic_id}: {e}")
                    continue

    def __enter__(self) -> "XKCDExtractor":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.session.close()
