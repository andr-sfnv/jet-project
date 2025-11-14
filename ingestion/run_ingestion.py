"""Run XKCD ingestion."""

import logging
import sys

import psycopg

from ingestion.extractor import XKCDExtractor
from ingestion.loader import XKCDLoader

logger = logging.getLogger(__name__)


def main():
    """Run incremental ingestion."""
    logger.info("Starting XKCD ingestion")

    try:
        with XKCDExtractor() as extractor, XKCDLoader() as loader:
            existing_ids = loader.get_existing_comic_ids()

            comics = list(extractor.fetch_missing_comics(existing_ids))

            if not comics:
                logger.info("No new comics - database is up to date")
                return

            logger.info(f"Found {len(comics)} new comics to load")

            loader.load_comics(comics)

    except (RuntimeError, psycopg.Error) as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

