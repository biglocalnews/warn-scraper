import datetime
import logging
import re
from os.path import exists
from pathlib import Path

import pdfplumber
import requests
import tenacity
import urllib3
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Florida Department of Economic Opportunity",
    "url": "http://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices",
}

logger = logging.getLogger(__name__)


FIELDS = [
    "Company Name",
    "State Notification Date",
    "Layoff Date",
    "Employees Affected",
    "Industry",
    "Attachment",
]
CSV_HEADERS = FIELDS[:-1]  # Clip the Attachment header


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Florida.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "fl.csv"
    cache = Cache(cache_dir)  # ~/.warn-scraper/cache
    # FL site requires realistic User-Agent.
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    url = "http://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices"
    response = requests.get(url, headers=headers, verify=False)
    logger.debug(f"Request status is {response.status_code} for {url}")
    soup = BeautifulSoup(response.text, "html.parser")
    # find & visit each year's WARN page
    base_url = "http://reactwarn.floridajobs.org/WarnList/"
    links = soup.find_all("a", href=re.compile(base_url))
    href_lookup = {_extract_year(link.text): link.get("href") for link in links}

    # Loop through years and add any missing to the lookup
    most_recent_year = int(list(href_lookup.keys())[0])
    earliest_year = 2015  # We expect files to be available for at least 2015
    for year in range(earliest_year, most_recent_year):
        if str(year) not in href_lookup:
            href_lookup[str(year)] = f"{base_url}viewPreviousYearsPDF?year={year}"

    output_rows = []
    # Loop through years and scrape data
    for year_url in href_lookup.values():
        if "PDF" in year_url:
            rows_to_add = _scrape_pdf(cache, cache_dir, year_url, headers)
        else:
            html_pages = _scrape_html(cache, year_url, headers)
            rows_to_add = _html_to_rows(html_pages)
        # Convert rows to dicts
        rows_as_dicts = [dict(zip(FIELDS, row)) for row in rows_to_add]
        output_rows.extend(rows_as_dicts)
    utils.write_dict_rows_to_csv(
        output_csv, CSV_HEADERS, output_rows, extrasaction="ignore"
    )
    return output_csv


# scrapes each html page for the current year
# returns a list of the year's html pages
# note: no max amount of retries (recursive scraping)
@tenacity.retry(
    wait=tenacity.wait_exponential(),
    retry=tenacity.retry_if_exception_type(requests.HTTPError),
)
def _scrape_html(cache, url, headers, page=1):
    urllib3.disable_warnings()  # sidestep SSL error
    # extract year from URL
    year = _extract_year(url)
    html_cache_key = f"fl/{year}_page_{page}.html"
    current_year = datetime.date.today().year
    last_year = str(current_year - 1)
    current_year = str(current_year)
    page_text = ""
    # search in cache first before scraping
    try:
        # re-scrape current year by default
        if not (year == current_year or year == last_year):
            logger.debug(f"Trying to read from cache: {html_cache_key}")
            cachefile = cache.read(html_cache_key)
            page_text = cachefile
            logger.debug(f"Page fetched from cache: {html_cache_key}")
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        # scrape & cache html
        response = requests.get(url, headers=headers, verify=False)
        logger.debug(f"Request status is {response.status_code} for {url}")
        response.raise_for_status()
        page_text = response.text
        cache.write(html_cache_key, page_text)
        logger.debug(f"Successfully scraped page {url} to cache: {html_cache_key}")
    page_text = page_text.replace("</br>", "\n")
    # search the page we just scraped for links to the next page
    soup = BeautifulSoup(page_text, "html.parser")
    footer = soup.find("tfoot")
    if footer:
        next_page = page + 1
        nextPageLink = footer.find(
            "a", href=re.compile(f"page={next_page}")
        )  # find link to next page, if exists
        # recursively scrape until we have a list of all the pages' html
        if nextPageLink:
            url = "http://reactwarn.floridajobs.org" + nextPageLink.get(
                "href"
            )  # /WarnList/Records?year=XXXX&page=X
            # recursively make list of all the next pages' html
            pages_html = _scrape_html(cache, url, headers, next_page)
            # add the current page to the recursive list
            pages_html.append(page_text)
            return pages_html
    # last page reached
    return [page_text]


def _html_to_rows(page_text):
    """Extract data rows from list of html pages."""
    output_rows = []
    for page in page_text:
        soup = BeautifulSoup(page, "html5lib")
        table = soup.find("table")
        # extract table data
        tbody = table.find("tbody")
        for table_row in tbody.find_all("tr"):
            columns = table_row.find_all("td")
            output_row = []
            for column in columns:
                output_row.append(column.text.strip())
            output_rows.append(output_row)
    return output_rows


# download and scrape pdf
@tenacity.retry(
    wait=tenacity.wait_exponential(),
    retry=tenacity.retry_if_exception_type(requests.HTTPError),
)
def _scrape_pdf(cache, cache_dir, url, headers):
    # sidestep SSL error
    urllib3.disable_warnings()
    # extract year from URL
    year = _extract_year(url)
    pdf_cache_key = f"fl/{year}.pdf"
    download = ""
    # download pdf if not in the cache
    if not exists(pdf_cache_key):
        response = requests.get(url, headers=headers, verify=False)
        logger.debug(f"Request status is {response.status_code} for {url}")
        response.raise_for_status()
        # download & cache pdf
        download = response.content
        with open(f"{cache_dir}/{pdf_cache_key}", "wb") as f:
            f.write(download)
        logger.debug(f"Successfully scraped PDF from {url} to cache: {pdf_cache_key}")
    # scrape tables from PDF
    with pdfplumber.open(f"{cache_dir}/{pdf_cache_key}") as pdf:
        pages = pdf.pages
        output_rows = []
        for page_num, page in enumerate(pages):
            table = page.extract_table(table_settings={})
            # remove each year's header
            if page_num == 0:
                table.pop(0)
            table = _clean_table(table, output_rows)
            output_rows.extend(table)  # merging lists
    logger.debug(f"Successfully scraped PDF from {url}")
    return output_rows


# adds split rows to output_rows by reference, returns list of page's rows to be added
def _clean_table(table, all_rows):
    table_rows = []
    for row_idx, row in enumerate(table):
        current_row = []
        # fix row splitting b/n pages sometimes
        if _is_multiline_row(row_idx, row):
            if (
                len(row) > 5
            ):  # fix where both row is split AND columns skewed right (like page 14 of 2016.pdf)
                row = [row[0], row[1], row[2], row[3], row[6]]
            for field_idx, field_to_add in enumerate(row):
                if field_to_add:
                    all_rows[-1][
                        field_idx
                    ] += field_to_add  # MERGE fields with last row from all_rows (i.e. the last row from prior page)
            continue
        for field_idx, field in enumerate(row):
            # ignore any redundant header rows
            if _is_header_row(field_idx, field):
                break
            # fix column skew by skipping blank columns
            if field:
                clean_field = field.strip()
                if clean_field:
                    current_row.append(clean_field)
        if current_row:
            table_rows.append(current_row)
    return table_rows


def _is_multiline_row(row_idx, row):
    # this is a row that has been split between pages
    # we want to remedy this split in the output data
    return row_idx == 0 and row[1] == "" and row[3] == ""


def _is_header_row(field_idx, field):
    # we already have a header management strategy
    # but there are still erroneous redundant headers strewn about
    # and we need to remove them from the data
    # because we only need 1 header row.
    return field_idx == 0 and field == "COMPANY NAME"


def _extract_year(text):
    """Extract the year from the string."""
    if text is None:
        return None
    return re.search(r"(\d{4})", text).group(1)


if __name__ == "__main__":
    scrape()
