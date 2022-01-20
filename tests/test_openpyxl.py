import pytest

from warn.scrapers import ia


@pytest.mark.vcr()
def test_iowa():
    ia.scrape()
