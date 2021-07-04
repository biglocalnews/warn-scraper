import re
from pathlib import Path

import pytest

from warn.platforms import JobCenterSite

@pytest.fixture
def site(cache_dir):
    url = 'https://www.kansasworks.com/search/warn_lookups'
    return JobCenterSite('KS', url, cache_dir)


@pytest.mark.vcr()
def test_scrape_integration(site):
    "should scrape by start and end dates"
    results_pages, data = site.scrape(
        start_date='2021-01-01',
        end_date='2021-03-08',
        detail_pages=True,
    )
    assert list(results_pages.keys()) == [1]
    assert isinstance(results_pages[1], str)
    assert len(data) == 2
    first = data[0]
    # Basics from search result pages
    assert first['employer'] == 'Waddell & Reed'
    assert first['city'] == 'Mission'
    assert first['zip'] == '66202'
    assert first['lwib_area'] == '3 - Workforce Investment Area III'
    assert first['notice_date'] ==  'Feb 26, 2021'
    assert first['warn_type'] == 'WARN'
    assert first['detail_page_url'] == 'https://www.kansasworks.com/search/warn_lookups/2135'
    # Additional data from record detail page
    details = first['detail']
    assert details['record_number'] == '2135'
    assert details['company_name'] == 'Waddell & Reed'
    assert details['address'] == '6300 Lamar Avenue\nMission, Kansas 66202'
    assert details['notice_date'] == 'Feb 26, 2021'
    assert details['number_of_employees_affected'] == 219
    assert 'html' in details.keys()

@pytest.mark.vcr()
def test_no_results(site):
    "should handle searches with no results"
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = site.scrape(
        start_date='1997-01-01',
        end_date='1997-12-31',
        detail_pages=False,
    )
    assert data == []
    assert results_pages == {}


@pytest.mark.vcr()
def test_missing_detail_page_values(site):
    "should handle detail pages missing one or more field values"
    results_pages, data = site.scrape(
        start_date='2020-07-31',
        end_date='2020-07-31',
        detail_pages=True,
    )
    detail = data[0]['detail']
    assert data[0]['employer'] == 'Spirit AeroSystems, Inc.'
    assert detail['company_name'] == 'Spirit AeroSystems, Inc.'
    # This record has a malformed date
    assert detail['notice_date'] == 'Jul 31, 2020'
    assert detail['number_of_employees_affected'] == 1100
    # Record is missing the address field
    assert detail['address'] == ''

@pytest.mark.vcr()
def test_paged_results(site):
    "should scrape all pages of results"
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = site.scrape(
        start_date='2020-05-01',
        end_date='2021-03-01',
        detail_pages=False,
    )
    assert len(data) == 27
    first = data[0]
    last = data[-1]
    assert first['employer'] == 'Spirit AeroSystems, Inc'
    assert last['employer'] == 'Waddell & Reed'


@pytest.mark.vcr()
def test_cached_search_results(tmp_path):
    "should save to cache when configured"
    url = 'https://www.kansasworks.com/search/warn_lookups'
    cache_dir = str(tmp_path.joinpath('ks'))
    site = JobCenterSite('KS', url, cache_dir=cache_dir)
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = site.scrape(
        start_date='2020-05-01',
        end_date='2021-03-01',
        detail_pages=False,
    )
    expected = [
        '2020-05-01_2021-03-01_page1.html',
        '2020-05-01_2021-03-01_page2.html'
    ]
    assert len(data) == 27
    files = [f.name for f in Path(cache_dir).glob('**/*.html')]
    assert len(files) == 2
    assert files == expected

@pytest.mark.vcr()
def test_cached_detail_pages(tmp_path):
    "should save to cache when configured"
    url = 'https://www.kansasworks.com/search/warn_lookups'
    cache_dir = str(tmp_path.joinpath('ks'))
    site = JobCenterSite('KS', url, cache_dir=cache_dir)
    # The dates below should span two pages (just barely).
    # Skip detail pages to minimize fixture size.
    results_pages, data = site.scrape(
        start_date='2021-02-01',
        end_date='2021-03-31',
        detail_pages=True,
    )
    assert len(data) == 2
    files = [f.name for f in Path(cache_dir).glob('**/*.html')]
    assert len(files) == 3
    # record files returned by glob resemble 1234.html (no records prefix)
    record_files = [f for f in files if re.match(r'\d{1,4}.html', f)]
    assert len(record_files) == 2
    assert Path(cache_dir, 'records').exists()
    assert Path(cache_dir, 'search_results').exists()
