import pytest

from warn.platforms import JobCenterSite

@pytest.fixture(scope='module')
def site():
    url = 'https://www.kansasworks.com/search/warn_lookups'
    return JobCenterSite('KS', url)


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
