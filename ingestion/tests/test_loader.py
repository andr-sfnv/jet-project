"""Tests for XKCD loader."""

from unittest.mock import Mock, patch

import pytest

from ingestion.extractor import XKCDComic
from ingestion.loader import DatabaseConfig, XKCDLoader


@pytest.fixture
def mock_config():
    """Mock database configuration."""
    return DatabaseConfig.model_validate(
        {
            "WAREHOUSE_HOST": "localhost",
            "WAREHOUSE_PORT": 5432,
            "WAREHOUSE_DB": "test_warehouse",
            "WAREHOUSE_USER": "test_user",
            "WAREHOUSE_PASSWORD": "test_password",
        }
    )


@pytest.fixture
def sample_comic():
    """Sample comic for testing."""
    return XKCDComic(
        num=1,
        title="Test Comic",
        safe_title="test_comic",
        alt="Test alt text",
        img="https://example.com/comic.png",
        transcript="Test transcript",
        year="2025",
        month="1",
        day="1",
        link="",
        news="",
    )


@pytest.fixture
def mock_connection():
    """Mock database connection and cursor."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
    return mock_conn, mock_cursor


def test_loader_context_manager(mock_config):
    """Test loader can be used as context manager."""
    loader = XKCDLoader(config=mock_config)

    with (
        patch.object(loader, "connect") as mock_connect,
        patch.object(loader, "disconnect") as mock_disconnect,
    ):
        with loader:
            pass

        mock_connect.assert_called_once()
        mock_disconnect.assert_called_once()


def test_load_comics_not_connected(mock_config, sample_comic):
    """Test load_comics raises RuntimeError when not connected."""
    loader = XKCDLoader(config=mock_config)

    with pytest.raises(RuntimeError, match="Not connected to database"):
        loader.load_comics([sample_comic])


def test_load_comics_single_batch(mock_config, sample_comic, mock_connection):
    """Test load_comics with a single batch."""
    loader = XKCDLoader(config=mock_config)
    mock_conn, mock_cursor = mock_connection
    loader.conn = mock_conn

    comics = [sample_comic]
    loader.load_comics(comics)

    mock_cursor.executemany.assert_called_once()
    mock_conn.commit.assert_called_once()


def test_load_comics_multiple_batches(mock_config, sample_comic, mock_connection):
    """Test load_comics with multiple batches."""
    loader = XKCDLoader(config=mock_config)
    mock_conn, mock_cursor = mock_connection
    loader.conn = mock_conn

    comics = [sample_comic] * 250
    loader.load_comics(comics, batch_size=100)

    assert mock_cursor.executemany.call_count == 3
    assert mock_conn.commit.call_count == 3


def test_get_existing_comic_ids_not_connected(mock_config):
    """Test get_existing_comic_ids raises RuntimeError when not connected."""
    loader = XKCDLoader(config=mock_config)

    with pytest.raises(RuntimeError, match="Not connected to database"):
        loader.get_existing_comic_ids()


def test_get_existing_comic_ids(mock_config, mock_connection):
    """Test get_existing_comic_ids returns set of comic IDs."""
    loader = XKCDLoader(config=mock_config)
    mock_conn, mock_cursor = mock_connection
    mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]
    loader.conn = mock_conn

    comic_ids = loader.get_existing_comic_ids()

    assert comic_ids == {1, 2, 3}
    mock_cursor.execute.assert_called_once_with("select comic_id from raw.xkcd_comics")
