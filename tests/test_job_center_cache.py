from pathlib import Path

import pytest

from warn.platforms.job_center.cache import Cache

from .conftest import write_file


@pytest.fixture
def cache_dir(tmp_path):
    """Create a path for a cache test."""
    return str(tmp_path.joinpath("ks"))


@pytest.mark.parametrize(
    "test_input",
    [
        # Initial search uses kwargs on base search url
        (
            "https://www.kansasworks.com/search/warn_lookups",
            {"q[notice_on_gteq]": "2020-05-01", "q[notice_on_lteq]": "2021-07-02"},
            "search_results/2020-05-01_2021-07-02_page1.html",
        ),
        # downstream search result page
        (
            "https://www.kansasworks.com/search/warn_lookups?commit=Search&page=2&q%5Bemployer_name_cont%5D=&q%5Bmain_contact_contact_info_addresses_full_location_city_matches%5D=&q%5Bnotice_eq%5D=true&q%5Bnotice_on_gteq%5D=2020-05-01&q%5Bnotice_on_lteq%5D=2021-07-02&q%5Bservice_delivery_area_id_eq%5D=&q%5Bzipcode_code_start%5D=&utf8=%E2%9C%93",
            {},
            "search_results/2020-05-01_2021-07-02_page2.html",
        ),
        # record page
        ("https://www.kansasworks.com/search/warn_lookups/123", {}, "records/123.html"),
    ],
)
def test_cache_key_from_url(test_input, cache_dir):
    """Test if the cache key is what's expected."""
    url, params, expected_key = test_input
    cache = Cache(cache_dir)
    cache_key = cache.key_from_url(url, params=params)
    assert cache_key == expected_key


@pytest.mark.parametrize(
    "test_input",
    [
        # downstream search result page
        (
            "https://www.kansasworks.com/search/warn_lookups?commit=Search&page=2&q%5Bemployer_name_cont%5D=&q%5Bmain_contact_contact_info_addresses_full_location_city_matches%5D=&q%5Bnotice_eq%5D=true&q%5Bnotice_on_gteq%5D=2020-05-01&q%5Bnotice_on_lteq%5D=2021-07-02&q%5Bservice_delivery_area_id_eq%5D=&q%5Bzipcode_code_start%5D=&utf8=%E2%9C%93",
            {},
            "search_results/2020-05-01_2021-07-02_page2.html",
        ),
        # record page
        ("https://www.kansasworks.com/search/warn_lookups/123", {}, "records/123.html"),
    ],
)
def test_cache_save(test_input, cache_dir):
    """Test saving data to the cache."""
    url, params, expected_name = test_input
    cache = Cache(cache_dir)
    cache.save(url, params, "<html><h1>Hello world</h1><html>")
    files = [str(f) for f in Path(cache_dir).glob("**/*.html")]
    assert len(files) == 1
    assert files[0].endswith(expected_name)


@pytest.mark.parametrize(
    "test_input",
    [
        # downstream search result page
        (
            "https://www.kansasworks.com/search/warn_lookups?commit=Search&page=2&q%5Bemployer_name_cont%5D=&q%5Bmain_contact_contact_info_addresses_full_location_city_matches%5D=&q%5Bnotice_eq%5D=true&q%5Bnotice_on_gteq%5D=2020-05-01&q%5Bnotice_on_lteq%5D=2021-07-02&q%5Bservice_delivery_area_id_eq%5D=&q%5Bzipcode_code_start%5D=&utf8=%E2%9C%93",
            {},
            "search_results/2020-05-01_2021-07-02_page2.html",
        ),
        # record page
        ("https://www.kansasworks.com/search/warn_lookups/123", {}, "records/123.html"),
    ],
)
def test_cache_fetch(test_input, cache_dir):
    """Test retrieving data from the cache."""
    url, params, name = test_input
    expected_content = "<html><h1>Hello world</h1><html>"
    dest = Path(cache_dir, name)
    write_file(dest, expected_content)
    cache = Cache(cache_dir)
    content = cache.fetch(url, params)
    assert content == expected_content
