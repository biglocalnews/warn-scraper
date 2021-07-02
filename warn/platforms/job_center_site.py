import html as html_mod
import logging
import requests
import urllib.parse
from datetime import date

import pandas as pd
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class JobCenterSite:
    """Scraper for America's Job Center sites.

    Job Center sites support date-based searches using
    a basic search form, such as for Kansas:

        https://www.kansasworks.com/search/warn_lookups/new

    Args:
        state (str): State postal code
        url (str): Base URL for the site
    """

    def __init__(self, state, url):
        self.state = state.upper()
        self.url = url

    def scrape(self, start_date=None, end_date=None, detail_pages=True):
        """Scrape between a particular start and end date.

        Defaults to scraping data for current year.

        Args:
            start_date (str): YYYY-MM-DD
            end_date (str): YYYY-MM-DD
            detail_pages (boolean, default True): Whether or not to scrape detail pages.

        Returns:

            An array containing a dictionary of html search result pages
            and a list of parsed data.

            ( {1: <HTML str>}, [<data>] )
        """
        # Final payload here
        html_store = {}
        data = []
        # Begin scrape of initial page
        start = start_date or self._start
        end = end_date or self._end
        params = self._search_kwargs(start_date=start, end_date=end)
        logger.debug(f"Scraping initial page for date range: {start_date} -> {end_date}")
        results = self._scrape_page(
            self.url,
            url_params=params,
            detail_pages=detail_pages
        )
        # Update the html_store and data payloads
        self._update_payload(html_store, data, results)
        # Scrape downstream pages, if any
        next_page_link = self._next_page_link(results['html'])
        if next_page_link:
            logger.debug("Scraping paged results")
            self._scrape_next_page(next_page_link, html_store, data, detail_pages)
        return (html_store, data)

    def _scrape_next_page(self, next_page_link, html_store, data, detail_pages):
        # Scrape the results of next page and update the payload
        results = self._scrape_page(next_page_link, detail_pages=detail_pages)
        self._update_payload(html_store, data, results)
        # If there are any more pages, make a recursive call
        next_page_link = self._next_page_link(results['html'])
        if next_page_link:
            self._scrape_next_page(next_page_link, html_store, data, detail_pages)
        # Otherwise, we've reached the last page so return
        else:
            return

    def _update_payload(self, html_store, data, results):
        # In-place updates
        page_num = results['page_num']
        html_store[page_num] = results['html']
        data.extend(results['data'])

    def _scrape_page(self, url, url_params={}, detail_pages=True):
        """Scrape data from search results page and detail pages.
        """
        # Downstream page URLs will have the "page" query parameter
        if 'page' in url:
            final_url = self._build_page_url(url)
            queries = urllib.parse.parse_qs(final_url)
            page_num = int(queries['page'][0]) # it's a one-element array
            html = self._get_page(final_url)
        # Whereas the initial page request doesn't have the "page" parameter
        else:
            page_num = 1
            html = self._get_page(url, params=url_params)
            logger.debug(url)
        data = self._parse_search_results(html)
        if detail_pages:
            logger.debug("Scraping detail pages for page...")
            for row in data:
                detail_page_data = self._scrape_detail_page(row['detail_page_url'])
                try:
                    row['detail'].update(detail_page_data)
                except ValueError:
                    breakpoint()
        return {
            'page_num': page_num,
            'html': html,
            'data': data
        }

    def _next_page_link(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        next_page = soup.find('a', class_="next_page")
        try:
            url_path = next_page['href']
            next_page_url = self._build_page_url(url_path)
        except TypeError:
            next_page_url = None
        return next_page_url

    def _get_page(self, url, params={}):
        response = requests.get(url, params=params)
        return response.text

    def _scrape_detail_page(self, url):
        logger.debug(url)
        html = self._get_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        company, address, notice_date, num_str= [
            val.text.strip() for val in soup.find('dl').find_all('dd')
        ]
        try:
            num_affected = int(num_str)
        except ValueError:
            num_affected = num_str
        return {
            'company_name': company,
            'address': address,
            'notice_date': notice_date,
            'number_of_employees_affected': num_affected,
            'html': html
        }

    def _parse_search_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        table_rows = soup.find_all('tr')
        # Remove header
        table_rows.pop(0)
        data = []
        # Process result listings
        for row in table_rows:
            row_data = self._extract_search_results_row(row)
            data.append(row_data)
        return data

    @property
    def _start(self):
        return f'{date.today().year}-01-01'

    @property
    def _end(self):
        month = str(date.today().month).zfill(2)
        day = month = str(date.today().day).zfill(2)
        return f'{today.year}-{month}-{day}'

    def _search_kwargs(self, start_date, end_date, extra={}):
        kwargs = {
            'utf8': '✓',
            'q[s]': 'notice_on asc', # sort chronologically
            'q[employer_name_cont]': '',
            'q[main_contact_contact_info_addresses_full_location_city_matches]': '',
            'q[zipcode_code_start]':'',
            'q[service_delivery_area_id_eq]':'',
            'q[notice_on_gteq]': start_date,
            'q[notice_on_lteq]': end_date,
            'q[notice_eq]': 'true',
            'commit': 'Search'
        }
        kwargs.update(extra)
        return kwargs

    def _extract_search_results_row(self, row):
        cells = row.find_all('td')
        url_path = cells[0].a['href'].strip()
        return {
            'employer': self._clean_field(cells[0].text),
            'city': cells[1].text.strip(),
            'zip': cells[2].text.strip(),
            'lwib_area': cells[3].text.strip(),
            'notice_date': cells[4].text.strip(),
            'warn_type': cells[5].text.strip(),
            'detail_page_url': self._build_page_url(url_path),
            'detail': {
                'record_number': url_path.rsplit('/')[-1],
            }
        }

    def _build_page_url(self, url_path):
        bits = urllib.parse.urlsplit(self.url)
        base_url = f'{bits.scheme}://{bits.netloc}'
        return urllib.parse.urljoin(base_url, url_path.strip())

    def _snake_case(self, text):
        return text.strip().lower().replace(' ', '_')

    def _clean_field(self, text):
        return html_mod.unescape(text.strip())
