"""XKCD Poller - Checks if new comics are available."""

import logging

import psycopg2

from ingestion.extractor import XKCDExtractor
from ingestion.loader import XKCDLoader

logger = logging.getLogger(__name__)


def check_new_comic_available() -> bool:
    """Check if a new comic is available on XKCD API."""
    try:
        with XKCDExtractor() as extractor:
            current_comic = extractor.fetch_current_comic()
            if current_comic is None:
                logger.warning("Could not fetch current comic from API")
                return False

            current_id = current_comic.num
            logger.info(f"Current comic ID from API: {current_id}")

        with XKCDLoader() as loader:
            existing_ids = loader.get_existing_comic_ids()
            max_existing_id = max(existing_ids) if existing_ids else 0
            logger.info(f"Max existing comic ID in database: {max_existing_id}")

            new_comic_available = current_id > max_existing_id
            if new_comic_available:
                logger.info(
                    f"New comic available! Current: {current_id}, Max in DB: {max_existing_id}"
                )
            else:
                logger.info(
                    f"No new comic yet. Current: {current_id}, Max in DB: {max_existing_id}"
                )

            return new_comic_available

    except (RuntimeError, psycopg2.Error) as e:
        logger.error(f"Failed to check for new comic: {e}", exc_info=True)
        return False


def should_skip_sensor(**context) -> str:
    """Determine whether to run sensor or skip it based on trigger type."""
    dag_run = context.get("dag_run")

    # Skip sensor if manually triggered
    if dag_run and dag_run.external_trigger:
        logger.info("Skipping sensor check (manually triggered run)")
        return "skip_sensor"

    return "wait_for_new_comic"
