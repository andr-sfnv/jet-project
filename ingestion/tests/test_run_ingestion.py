"""Tests for run_ingestion module."""

from unittest.mock import Mock, patch

import pytest

from ingestion.extractor import XKCDComic, XKCDExtractor
from ingestion.loader import XKCDLoader


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


def test_main_no_new_comics(sample_comic):
    """Test main() when no new comics are found."""
    with (
        patch("ingestion.run_ingestion.XKCDExtractor") as mock_extractor_class,
        patch("ingestion.run_ingestion.XKCDLoader") as mock_loader_class,
    ):
        mock_extractor = Mock(spec=XKCDExtractor)
        mock_loader = Mock(spec=XKCDLoader)
        mock_extractor_class.return_value.__enter__ = Mock(return_value=mock_extractor)
        mock_extractor_class.return_value.__exit__ = Mock(return_value=None)
        mock_loader_class.return_value.__enter__ = Mock(return_value=mock_loader)
        mock_loader_class.return_value.__exit__ = Mock(return_value=None)

        mock_loader.get_existing_comic_ids.return_value = {1, 2, 3}
        mock_extractor.fetch_comics.return_value = []

        from ingestion.run_ingestion import main

        main()

        mock_loader.get_existing_comic_ids.assert_called_once()
        mock_extractor.fetch_comics.assert_called_once_with({1, 2, 3})
        mock_loader.load_comics.assert_not_called()


def test_main_with_new_comics(sample_comic):
    """Test main() when new comics are found."""
    with (
        patch("ingestion.run_ingestion.XKCDExtractor") as mock_extractor_class,
        patch("ingestion.run_ingestion.XKCDLoader") as mock_loader_class,
    ):
        mock_extractor = Mock(spec=XKCDExtractor)
        mock_loader = Mock(spec=XKCDLoader)
        mock_extractor_class.return_value.__enter__ = Mock(return_value=mock_extractor)
        mock_extractor_class.return_value.__exit__ = Mock(return_value=None)
        mock_loader_class.return_value.__enter__ = Mock(return_value=mock_loader)
        mock_loader_class.return_value.__exit__ = Mock(return_value=None)

        mock_loader.get_existing_comic_ids.return_value = {1, 2}
        mock_extractor.fetch_comics.return_value = [sample_comic]

        from ingestion.run_ingestion import main

        main()

        mock_loader.get_existing_comic_ids.assert_called_once()
        mock_extractor.fetch_comics.assert_called_once_with({1, 2})
        mock_loader.load_comics.assert_called_once_with([sample_comic])


def test_main_handles_runtime_error(sample_comic):
    """Test main() handles RuntimeError."""
    with (
        patch("ingestion.run_ingestion.XKCDExtractor") as mock_extractor_class,
        patch("ingestion.run_ingestion.XKCDLoader") as mock_loader_class,
        patch("ingestion.run_ingestion.sys.exit") as mock_exit,
    ):
        mock_extractor = Mock(spec=XKCDExtractor)
        mock_loader = Mock(spec=XKCDLoader)
        mock_extractor_class.return_value.__enter__ = Mock(return_value=mock_extractor)
        mock_extractor_class.return_value.__exit__ = Mock(return_value=None)
        mock_loader_class.return_value.__enter__ = Mock(return_value=mock_loader)
        mock_loader_class.return_value.__exit__ = Mock(return_value=None)

        mock_loader.get_existing_comic_ids.side_effect = RuntimeError("Database error")

        from ingestion.run_ingestion import main

        main()

        mock_exit.assert_called_once_with(1)
