import pytest

from warn.scrapers import ia


@pytest.mark.vcr()
def test_iowa():
    """Test openpyxl bits with Iowa scraper."""
    ia.scrape()
