"""PostgreSQL Loader - Loads XKCD comic data into the database."""

import json
import logging
import uuid
from datetime import UTC, datetime

import psycopg
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ingestion.extractor import XKCDComic

logger = logging.getLogger(__name__)


class DatabaseConfig(BaseSettings):
    """Database connection configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
    )

    warehouse_host: str = Field(default="localhost", alias="WAREHOUSE_HOST")
    warehouse_port: int = Field(default=5432, alias="WAREHOUSE_PORT")
    warehouse_db: str = Field(default="warehouse", alias="WAREHOUSE_DB")
    warehouse_user: str = Field(default="analytics", alias="WAREHOUSE_USER")
    warehouse_password: str = Field(default="analytics", alias="WAREHOUSE_PASSWORD")


class XKCDLoader:
    """Load XKCD comic data into PostgreSQL warehouse."""

    def __init__(self, config: DatabaseConfig | None = None):
        """Initialize loader with database configuration."""
        self.config = config if config is not None else DatabaseConfig()
        self.conn: psycopg.Connection | None = None

    def connect(self) -> None:
        """Establish database connection and create tables if needed."""
        if self.conn is not None:
            logger.warning("Already connected, skipping connection")
            return

        logger.info("Connecting to database")
        self.conn = psycopg.connect(
            host=self.config.warehouse_host,
            port=self.config.warehouse_port,
            dbname=self.config.warehouse_db,
            user=self.config.warehouse_user,
            password=self.config.warehouse_password,
        )

        with self.conn.cursor() as cur:
            cur.execute("create schema if not exists raw")
            cur.execute(
                """
                create table if not exists raw.xkcd_comics (
                    comic_id integer primary key,
                    raw_json jsonb not null,
                    load_ts timestamp not null default current_timestamp,
                    load_id uuid not null
                )
                """
            )
            cur.execute(
                "create index if not exists idx_xkcd_comics_load_ts on raw.xkcd_comics(load_ts)"
            )
            cur.execute(
                "create index if not exists idx_xkcd_comics_load_id on raw.xkcd_comics(load_id)"
            )
            self.conn.commit()

        logger.info("Database connection established")

    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")

    def load_comics(self, comics: list[XKCDComic], batch_size: int = 100) -> None:
        """Load multiple comics in batches."""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        load_id = uuid.uuid4()
        load_ts = datetime.now(UTC)

        for i in range(0, len(comics), batch_size):
            batch = comics[i : i + batch_size]
            batch_data = [
                (
                    comic.num,
                    json.dumps(comic.model_dump()),
                    load_ts,
                    load_id,
                )
                for comic in batch
            ]

            with self.conn.cursor() as cur:
                cur.executemany(
                    """
                    insert into raw.xkcd_comics (comic_id, raw_json, load_ts, load_id)
                    values (%s, %s, %s, %s)
                    on conflict (comic_id) do update
                    set raw_json = excluded.raw_json,
                        load_ts = excluded.load_ts,
                        load_id = excluded.load_id
                    """,
                    batch_data,
                )
                self.conn.commit()

    def get_existing_comic_ids(self) -> set[int]:
        """Get set of all comic IDs already in the database."""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        with self.conn.cursor() as cur:
            cur.execute("select comic_id from raw.xkcd_comics")
            rows = cur.fetchall()
            comic_ids = {row[0] for row in rows}
            logger.info(f"Found {len(comic_ids)} existing comics in database")
            return comic_ids

    def __enter__(self) -> "XKCDLoader":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()
