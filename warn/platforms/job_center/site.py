import html as html_mod
import logging
import urllib.parse
from datetime import date

import requests
from bs4 import BeautifulSoup

from .cache import Cache
from .urls import urls

logger = logging.getLogger(__name__)


class NoSearchResultsError(Exception):
    """Thrown when there are no results."""

    pass


class Site:
    """Scraper for America's Job Center sites.

    Job Center support date-based searches via a search URL.
    Below is an example URL for Kansas:

        https://www.kansasworks.com/search/warn_lookups

    Args:
        state (str): State postal code
        url (str): Search URL for the site (should end in '/warn_lookups')
        cache_dir (str): Cache directory
    """

    def __init__(self, state, url, cache_dir):
        """Initialize a new instance."""
        self.state = state.upper()
        self.url = url
        self.cache = Cache(cache_dir)

    def scrape(self, start_date=None, end_date=None, detail_pages=True, use_cache=True):
        """
        Scrape between a start and end date.

        Defaults to scraping data for current year.

        Args:
            start_date (str): YYYY-MM-DD
            end_date (str): YYYY-MM-DD
            detail_pages (boolean, default True): Whether or not to scrape detail pages.
            use_cache (boolean, default True): Check cache before scraping.

        Returns:
            An array containing a dictionary of html search result pages
            and a list of parsed data dictionaries
            ( {1: <HTML str>}, [{data}, {more data}] )
        """
        # Final payload here
        html_store = {}
        data = []
        # Begin scrape with initial page
        start = start_date or self._start
        end = end_date or self._end
        kwargs = {
            "params": self._search_kwargs(start_date=start, end_date=end),
            "use_cache": use_cache,
            "detail_pages": detail_pages,
        }
        logger.debug(
            f"Scraping initial page for date range: {start_date} -> {end_date}"
        )
        results = self._scrape_search_results_page(self.url, **kwargs)
        # Exit early if there were no results
        if not results.get("data"):
            return (html_store, data)
        # Update the html_store and data payloads
        self._update_payload(html_store, data, results)
        # Scrape downstream pages, if any
        next_page_link = self._next_page_link(results["html"])
        if next_page_link:
            logger.debug("Scraping paged results")
            self._scrape_next_page(
                next_page_link, html_store, data, detail_pages, use_cache
            )
        return (html_store, data)

    @property
    def _start(self):
        """Get the start date."""
        return f"{date.today().year}-01-01"

    @property
    def _end(self):
        """Get the end date."""
        today = date.today()
        month = str(today.month).zfill(2)
        day = str(today.day).zfill(2)
        return f"{today.year}-{month}-{day}"

    def _get_page(self, url, params=None, use_cache=True):
        """
        Fetch page from cache or scrape anew.

        Defaults to using cached page if it exists. Always caches freshly scraped page.
        """
        logger.debug(f"Requesting {url}")
        cache_key = self.cache.key_from_url(url, params)
        if use_cache and self.cache.exists(cache_key):
            logger.debug("Fetching from cache")
            return self.cache.fetch(url, params)
        else:
            logger.debug("Pulling from the web")
            response = requests.get(url, params=params)
            logger.debug(f"Response code: {response.status_code}")
            html = response.text
            self.cache.save(url, params, html)
            return html

    def _scrape_search_results_page(
        self, url, params=None, detail_pages=True, use_cache=True
    ):
        """Scrape data from search results page and detail pages."""
        kwargs = {"params": params, "use_cache": use_cache}
        # Downstream page URLs will have the "page" query parameter
        if "page" in url:
            final_url = self._build_page_url(url)
            page_num = urls.page_num_from_url(final_url)
            html = self._get_page(final_url, **kwargs)
        # Whereas the initial page request doesn't have the "page" parameter
        else:
            page_num = 1
            html = self._get_page(url, **kwargs)
        try:
            data = self._parse_search_results(html)
        except NoSearchResultsError:
            return {}
        if detail_pages:
            logger.debug("Scraping detail pages found on search results page...")
            for row in data:
                detail_page_data = self._scrape_detail_page(
                    row["detail_page_url"], use_cache
                )
                row["detail"].update(detail_page_data)
        return {"page_num": page_num, "html": html, "data": data}

    def _scrape_next_page(
        self, next_page_link, html_store, data, detail_pages, use_cache
    ):
        """Scrape the results of next page and update the payload."""
        kwargs = {
            "params": {},
            "detail_pages": detail_pages,
            "use_cache": use_cache,
        }
        results = self._scrape_search_results_page(next_page_link, **kwargs)
        try:
            results["data"]
        # Empty results dict signals no search results were returned
        except KeyError:
            return
        self._update_payload(html_store, data, results)
        # If there are any more pages, make a recursive call
        next_page_link = self._next_page_link(results["html"])
        if next_page_link:
            args = [next_page_link, html_store, data, detail_pages, use_cache]
            self._scrape_next_page(*args)
        # Otherwise, we've reached the last page so return
        else:
            return

    def _scrape_detail_page(self, url, use_cache):
        """Scrape the provided detail page."""
        html = self._get_page(url, use_cache=use_cache)
        return self._parse_detail_page(html)

    def _parse_detail_page(self, html):
        """Parse data out of a detail page."""
        payload = {
            "company_name": "",
            "address": "",
            "number_of_employees_affected": "",
            "notice_date": "",
        }
        soup = BeautifulSoup(html, "html.parser")
        headers = [
            self._snake_case(header.text)
            for header in soup.select(".definition-list__title")
        ]
        values = [
            field.text.strip() for field in soup.select(".definition-list__definition")
        ]
        data = dict(zip(headers, values))
        payload.update(data)
        payload["html"] = html
        return payload

    def _parse_search_results(self, html):
        """Parse data out of the search results."""
        data = []
        soup = BeautifulSoup(html, "html.parser")
        table_rows = soup.find_all("tr")
        # Remove header
        try:
            table_rows.pop(0)
        except IndexError:
            # IndexError signals no results were found on page
            # Verify this page has no results and return data
            msg = "no matches for your search results"
            if msg in soup.text:
                raise NoSearchResultsError(msg)
        # Process result listings
        for row in table_rows:
            row_data = self._extract_search_results_row(row)
            data.append(row_data)
        return data

    def _update_payload(self, html_store, data, results):
        """Update a payload."""
        # In-place updates
        page_num = results.get("page_num")
        if page_num:
            html_store[page_num] = results["html"]
        data.extend(results.get("data", []))

    def _search_kwargs(self, start_date, end_date, extra=None):
        """Set keyword arguments for a search."""
        kwargs = {
            "utf8": "✓",
            "q[employer_name_cont]": "",
            "q[main_contact_contact_info_addresses_full_location_city_matches]": "",
            "q[zipcode_code_start]": "",
            "q[service_delivery_area_id_eq]": "",
            "q[notice_on_gteq]": start_date,
            "q[notice_on_lteq]": end_date,
            "q[notice_eq]": "",
            "commit": "Search",
        }
        if extra:
            kwargs.update(extra)
        return kwargs

    def _extract_search_results_row(self, row):
        """Parse out results from a row of search results."""
        cells = row.find_all("td")
        url_path = cells[0].a["href"].strip()
        return {
            "employer": self._clean_field(cells[0].text),
            "city": cells[1].text.strip(),
            "zip": cells[2].text.strip(),
            "lwib_area": cells[3].text.strip(),
            "notice_date": cells[4].text.strip(),
            "warn_type": cells[5].text.strip(),
            "detail_page_url": self._build_page_url(url_path),
            "detail": {
                "record_number": url_path.rsplit("/")[-1],
            },
        }

    def _next_page_link(self, html):
        """Get the link for the next page, if it exists."""
        soup = BeautifulSoup(html, "html.parser")
        next_page = soup.find("a", class_="next_page")
        try:
            url_path = next_page["href"]
            next_page_url = self._build_page_url(url_path)
        except TypeError:
            next_page_url = None
        return next_page_url

    def _build_page_url(self, url_path):
        """Create the URL for the page."""
        bits = urllib.parse.urlsplit(self.url)
        base_url = f"{bits.scheme}://{bits.netloc}"
        return urllib.parse.urljoin(base_url, url_path.strip())

    def _snake_case(self, text):
        """Convert text to SnakeCase."""
        return text.strip().lower().replace(" ", "_")

    def _clean_field(self, text):
        """Strip and tidy a line of text."""
        return html_mod.unescape(text.strip())
