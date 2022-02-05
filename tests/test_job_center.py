import re
from pathlib import Path

import pytest

from warn.platforms import JobCenterSite


@pytest.fixture
def ks_site(cache_dir):
    """Create a fixture from the Kansas site."""
    url = "https://www.kansasworks.com/search/warn_lookups"
    return JobCenterSite("KS", url, cache_dir)


@pytest.fixture
def ok_site(cache_dir):
    """Create a fixture from the Oklahoma site."""
    url = "https://okjobmatch.com/search/warn_lookups"
    return JobCenterSite("OK", url, cache_dir)


@pytest.mark.vcr()
def test_scrape_integration(ok_site):
    """Test a scraper."""
    # should scrape by start and end dates
    results_pages, data = ok_site.scrape(
        start_date="2021-01-01",
        end_date="2021-02-03",
        detail_pages=True,
    )
    assert list(results_pages.keys()) == [1]
    assert isinstance(results_pages[1], str)
    assert len(data) == 2
    first = data[0]
    # Basics from search result pages
    assert first["employer"] == "Exterran Energy Solutions"
    assert first["city"] == "Broken Arrow"
    assert first["zip"] == "74014"
    assert first["lwib_area"] == "12 - TulsaRegion"
    assert first["notice_date"] == "Jan 13, 2021"
    assert first["warn_type"] == "WARN"
    assert first["detail_page_url"] == "https://okjobmatch.com/search/warn_lookups/780"
    # Additional data from record detail page
    details = first["detail"]
    assert details["record_number"] == "780"
    assert details["company_name"] == "Exterran Energy Solutions"
    assert details["address"] == "20602 E. 81st Street\nBroken Arrow, Oklahoma 74014"
    assert details["notice_date"] == "Jan 13, 2021"
    assert details["number_of_employees_affected"] == "0"
    assert "html" in details.keys()


@pytest.mark.vcr()
def test_no_results(ks_site):
    """Test an instance where there are no results."""
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = ks_site.scrape(
        start_date="1997-01-01",
        end_date="1997-12-31",
        detail_pages=False,
    )
    assert data == []
    assert results_pages == {}


@pytest.mark.vcr()
def test_missing_detail_page_values(ks_site):
    """Test a case where detail pages are missing one or more field values."""
    results_pages, data = ks_site.scrape(
        start_date="2020-07-31",
        end_date="2020-07-31",
        detail_pages=True,
    )
    detail = data[0]["detail"]
    assert data[0]["employer"] == "Spirit AeroSystems, Inc."
    assert detail["company_name"] == "Spirit AeroSystems, Inc."
    # This record has a malformed date
    assert detail["notice_date"] == "Jul 31, 2020"
    assert detail["number_of_employees_affected"] == "1100"
    # Record is missing the address field
    assert detail["address"] == ""


@pytest.mark.vcr()
def test_paged_results(ok_site):
    """Test a case with paginated results."""
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = ok_site.scrape(
        start_date="2020-01-01",
        end_date="2020-04-30",
        detail_pages=False,
    )
    assert len(data) == 42
    first = data[0]
    last = data[-1]
    assert first["employer"] == "Vallourec Star, LP"
    assert last["employer"] == "Uncle Julio's"


@pytest.mark.vcr()
def test_cached_search_results(tmp_path):
    """Test a case when the cache should be used for search results."""
    url = "https://okjobmatch.com/search/warn_lookups"
    cache_dir = str(tmp_path.joinpath("ok"))
    site = JobCenterSite("OK", url, cache_dir=cache_dir)
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = site.scrape(
        start_date="2020-01-01",
        end_date="2020-04-15",
        detail_pages=False,
    )
    expected = ["2020-01-01_2020-04-15_page1.html", "2020-01-01_2020-04-15_page2.html"]
    files = [f.name for f in Path(cache_dir).glob("**/*.html")]
    assert len(files) == 2
    assert sorted(files) == sorted(expected)


@pytest.mark.vcr()
def test_cached_detail_pages(tmp_path):
    """Test a case when the cache should be used for detail pages."""
    url = "https://okjobmatch.com/search/warn_lookups"
    cache_dir = str(tmp_path.joinpath("ok"))
    site = JobCenterSite("OK", url, cache_dir=cache_dir)
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = site.scrape(
        start_date="2021-01-01",
        end_date="2021-02-03",
        detail_pages=True,
    )
    assert len(data) == 2
    files = [f.name for f in Path(cache_dir).glob("**/*.html")]
    assert len(files) == 3
    # record files returned by glob resemble 1234.html (no records prefix)
    record_files = [f for f in files if re.match(r"\d{1,4}.html", f)]
    assert len(record_files) == 2
    assert Path(cache_dir, "records").exists()
    assert Path(cache_dir, "search_results").exists()
