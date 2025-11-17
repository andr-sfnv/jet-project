"""Tests for XKCD poller."""

from unittest.mock import MagicMock, patch

import pytest

from ingestion.poller import check_new_comic_available, should_skip_sensor


@pytest.fixture
def mock_extractor():
    """Mock XKCDExtractor."""
    with patch("ingestion.poller.XKCDExtractor") as mock:
        extractor_instance = MagicMock()
        mock.return_value.__enter__.return_value = extractor_instance
        mock.return_value.__exit__.return_value = None
        yield extractor_instance


@pytest.fixture
def mock_loader():
    """Mock XKCDLoader."""
    with patch("ingestion.poller.XKCDLoader") as mock:
        loader_instance = MagicMock()
        mock.return_value.__enter__.return_value = loader_instance
        mock.return_value.__exit__.return_value = None
        yield loader_instance


def test_check_new_comic_available_when_new_comic_exists(mock_extractor, mock_loader):
    """Test that check_new_comic_available returns True when new comic exists."""
    from ingestion.extractor import XKCDComic

    current_comic = XKCDComic(
        num=100,
        title="Test Comic",
        safe_title="Test Comic",
        alt="Alt text",
        img="https://example.com/img.png",
        year="2025",
        month="1",
        day="1",
    )
    mock_extractor.fetch_current_comic.return_value = current_comic
    mock_loader.get_existing_comic_ids.return_value = {1, 2, 3, 50}

    result = check_new_comic_available()

    assert result is True
    mock_extractor.fetch_current_comic.assert_called_once()
    mock_loader.get_existing_comic_ids.assert_called_once()


def test_check_new_comic_available_when_no_new_comic(mock_extractor, mock_loader):
    """Test that check_new_comic_available returns False when no new comic exists."""
    from ingestion.extractor import XKCDComic

    current_comic = XKCDComic(
        num=50,
        title="Test Comic",
        safe_title="Test Comic",
        alt="Alt text",
        img="https://example.com/img.png",
        year="2025",
        month="1",
        day="1",
    )
    mock_extractor.fetch_current_comic.return_value = current_comic
    mock_loader.get_existing_comic_ids.return_value = {1, 2, 3, 50}

    result = check_new_comic_available()

    assert result is False
    mock_extractor.fetch_current_comic.assert_called_once()
    mock_loader.get_existing_comic_ids.assert_called_once()


def test_check_new_comic_available_when_no_comics_in_db(mock_extractor, mock_loader):
    """Test that check_new_comic_available returns True when database is empty."""
    from ingestion.extractor import XKCDComic

    current_comic = XKCDComic(
        num=1,
        title="Test Comic",
        safe_title="Test Comic",
        alt="Alt text",
        img="https://example.com/img.png",
        year="2025",
        month="1",
        day="1",
    )
    mock_extractor.fetch_current_comic.return_value = current_comic
    mock_loader.get_existing_comic_ids.return_value = set()

    result = check_new_comic_available()

    assert result is True
    mock_extractor.fetch_current_comic.assert_called_once()
    mock_loader.get_existing_comic_ids.assert_called_once()


def test_check_new_comic_available_when_api_returns_none(mock_extractor, mock_loader):
    """Test that check_new_comic_available returns False when API returns None."""
    mock_extractor.fetch_current_comic.return_value = None

    result = check_new_comic_available()

    assert result is False
    mock_extractor.fetch_current_comic.assert_called_once()
    mock_loader.get_existing_comic_ids.assert_not_called()


def test_should_skip_sensor_when_manually_triggered():
    """Test that should_skip_sensor returns skip_sensor when manually triggered."""
    mock_dag_run = MagicMock()
    mock_dag_run.external_trigger = True
    context = {"dag_run": mock_dag_run}

    result = should_skip_sensor(**context)

    assert result == "skip_sensor"


def test_should_skip_sensor_when_scheduled():
    """Test that should_skip_sensor returns wait_for_new_comic when scheduled."""
    mock_dag_run = MagicMock()
    mock_dag_run.external_trigger = False
    context = {"dag_run": mock_dag_run}

    result = should_skip_sensor(**context)

    assert result == "wait_for_new_comic"
