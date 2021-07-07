import datetime
import logging
import re
import requests
import urllib3

from bs4 import BeautifulSoup
# import pdfplumber
import tenacity

from warn.cache import Cache
from warn.utils import write_rows_to_csv

logger = logging.getLogger(__name__)

# scrape all links from WARN page http://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices


def scrape(output_dir, cache_dir=None):
    output_csv = '{}/fl.csv'.format(output_dir)
    cache = Cache(cache_dir)  # ~/.warn-scraper/cache
    # FL site requires realistic User-Agent.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    url = 'http://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices'
    response = requests.get(url, headers=headers, verify=False)
    logger.debug(f"Request status is {response.status_code} for {url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    # find & visit each year's WARN page
    links = soup.find_all('a', href=re.compile('^http://reactwarn.floridajobs.org/WarnList/'))
    output_rows = []
    header_written = False
    # scraped most recent year first
    for year_url in links:
        year_url = year_url.get('href')  # get URL from link
        logger.debug(f'{year_url}')
        if 'PDF' in year_url:
            rows_to_add = scrape_pdf(cache, year_url, headers)
            logger.warning(f'PDF functionality not implemented for page {year_url}')
        else:
            html_pages = scrape_html(cache, year_url, headers)
            logger.debug(f"html_pages for {year_url} has item lengths of {[len(i) for i in html_pages]} ")
            # write the header only once
            if not header_written:
                output_rows.append(write_header(html_pages))
                header_written = True
            rows_to_add = html_to_rows(html_pages, output_csv)
        [output_rows.append(row) for row in rows_to_add]  # moving from one list to the other
    logger.debug(f"len output rows: {len(output_rows)}")
    write_rows_to_csv(output_rows, output_csv)
    return output_csv

# scrapes each html page for the current year
# returns a list of the year's html pages
# note: no max amount of retries due to recursive scraping


@tenacity.retry(wait=tenacity.wait_exponential(),
                retry=tenacity.retry_if_exception_type(requests.HTTPError))
def scrape_html(cache, url, headers, page=1):
    # sidestep SSL error
    urllib3.disable_warnings()
    # extract year from URL
    year = re.search(r'year=([0-9]{4})', url, re.I).group(1)
    html_cache_key = f'fl/{year}_page_{page}'
    current_year = datetime.date.today().year
    last_year = str(current_year - 1)
    current_year = str(current_year)
    page_text = ""
    # search in cache first before scraping
    try:
        # always re-scrape current year and prior year just to be safe
        # note that this strategy, while safer, spends a long time scraping 2020.
        if not (year == current_year) and not (year == last_year):
            logger.debug(f'Trying to read from cache: {html_cache_key}')
            cachefile = cache.read(html_cache_key)
            page_text = cachefile
            logger.debug(f'Page fetched from cache: {html_cache_key}')
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        response = requests.get(url, headers=headers, verify=False)
        logger.debug(f"Request status is {response.status_code} for {url}")
        response.raise_for_status()
        page_text = response.text
        cache.write(html_cache_key, page_text)
        logger.debug(f"Successfully scraped page {url} to cache: {html_cache_key}")
    # search the page we just scraped for links to the next page
    soup = BeautifulSoup(page_text, 'html.parser')
    footer = soup.find('tfoot')
    if footer:
        next_page = page + 1
        nextPageLink = footer.find('a', href=re.compile(f'page={next_page}'))  # find link to next page, if exists
        # recursively scrape to the last page
        if nextPageLink:
            url = 'http://reactwarn.floridajobs.org' + nextPageLink.get('href')  # /WarnList/Records?year=XXXX&page=X
            # recursively make list of all the next pages' html
            pages_html = scrape_html(cache, url, headers, next_page)
            # add the current page to the recursive list
            pages_html.append(page_text)
            return pages_html
    # last page reached
    return [page_text]


# takes list of html pages, outputs list of rows
def html_to_rows(page_text, output_csv):
    output_rows = []
    for page in page_text:
        soup = BeautifulSoup(page, 'html5lib')
        table = soup.find('table')
        # extract table data
        tbody = table.find('tbody')
        for table_row in tbody.find_all('tr'):
            columns = table_row.find_all('td')
            output_row = []
            for column in columns:
                output_row.append(column.text.strip())
            output_rows.append(output_row)
        output_rows.pop(0)  # remove blank lines
        # output_rows.pop(0)
    return output_rows


# extract table headers, only once
def write_header(pages):
    page = pages[0]
    soup = BeautifulSoup(page, 'html5lib')
    table = soup.find('table')
    thead = table.find('thead')
    headers = thead.find_all('th')
    output_rows = []
    for header in headers:
        output_rows.append(header.text.strip())
    return output_rows


# try: find pdf in cache.
# except: download pdf, store in cache
# then: process in pandas(?)
# return as output_rows??
def scrape_pdf(cache, url, headers):
    # response = requests.get(url, headers=headers, verify=False)
    # logger.debug(f"Request status is {response.status_code} for {url}")
    # response.raise_for_status()
    # with pdfplumber.open("path/to/file.pdf") as pdf:
    #     pages = pdf.pages[0]
    #     processed_pdf = pages  # TODO PDF Plumber code
    # logger.debug(f"Successfully scraped PDF from {url}")
    pdf_rows = []
    return pdf_rows
