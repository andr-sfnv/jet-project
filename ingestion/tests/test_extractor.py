"""Tests for XKCD extractor."""

import pytest
from unittest.mock import Mock, patch
from ingestion.extractor import XKCDExtractor, XKCDComic


@pytest.fixture
def mock_comic_data():
    """Sample comic data for testing."""
    return {
        "num": 1,
        "title": "Barrel - Part 1",
        "safe_title": "Barrel - Part 1",
        "alt": "Don't we all.",
        "img": "https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg",
        "transcript": "Test transcript",
        "year": "2006",
        "month": "1",
        "day": "1",
        "link": "",
        "news": "",
    }


@pytest.fixture
def extractor():
    """Create extractor instance."""
    return XKCDExtractor()


def test_xkcd_comic_model(mock_comic_data):
    """Test XKCDComic model validation."""
    comic = XKCDComic(**mock_comic_data)
    assert comic.num == 1
    assert comic.title == "Barrel - Part 1"
    assert comic.year == "2006"


def test_fetch_current_comic_success(extractor, mock_comic_data):
    """Test fetching current comic successfully."""
    with patch.object(extractor.session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_comic_data
        mock_get.return_value = mock_response

        comic = extractor.fetch_current_comic()

        assert comic is not None
        assert comic.num == 1
        assert comic.title == "Barrel - Part 1"


def test_fetch_comic_by_id_not_found(extractor):
    """Test fetching non-existent comic returns None."""
    with patch.object(extractor.session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        comic = extractor.fetch_comic_by_id(99999)
        assert comic is None


def test_context_manager(extractor):
    """Test extractor can be used as context manager."""
    with extractor as ext:
        assert ext is not None

