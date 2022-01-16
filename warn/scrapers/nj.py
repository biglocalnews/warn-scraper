import typing
import logging
import itertools
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from New Jersey.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "nj.csv"
    url = "http://lwd.state.nj.us/WorkForceDirectory/warn.jsp"
    logger.debug(f"Scraping {url}")
    html = _scrape_page(url)
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")  # output is list-type
    # The header and each line of company data lives in its own table.
    # Old school.
    header_table = tables.pop(0)
    headers = _extract_fields_from_table(header_table)
    output_rows = [headers]
    # Process company "rows"
    for table in tables:
        layoff_data_row = _extract_fields_from_table(table)
        output_rows.append(layoff_data_row)
    # Perform initial write of data
    utils.write_rows_to_csv(output_rows, output_csv)
    cache = Cache(cache_dir)  # ~/.warn-scraper/cache
    _scrape_2010_to_2004(cache, output_csv)
    _dedupe(output_csv)
    return output_csv


def _scrape_page(url):
    response = utils.get_url(url)
    response.encoding = "utf-8"
    return response.text


def _extract_fields_from_table(table):
    row = table.find_all("tr")[0]
    data = []
    for field in row.find_all("td"):
        data.append(field.text.strip())
    return data


def _scrape_2010_to_2004(cache, output_csv):
    years = [2010, 2009, 2008, 2007, 2006, 2005, 2004]
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    year_month_pairs = itertools.product(years, months)  # [(2010, 'Jan'), ...]
    for year, month in year_month_pairs:
        html_page_name = f"{month}{year}Warn.html"
        # Add the state postal as cache key prefix
        cache_key = f"nj/{html_page_name}"
        try:
            html = cache.read(cache_key)
            logger.debug(f"Page fetched from cache: {cache_key}")
        except FileNotFoundError:
            # If file not found in cache, scrape the page and save to cache
            url = f"https://www.nj.gov/labor/lwdhome/warn/{year}/{html_page_name}"
            html = _scrape_page(url)
            cache.write(cache_key, html)
            logger.debug(f"Scraped and cached {url}")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all("table")  # output is list-type
        output_rows = []
        for tr in table[0].find_all("tr"):
            row_data = [field.text.strip() for field in tr.find_all("td")]
            output_rows.append(row_data)
        # Remove header row
        output_rows.pop(0)
        if len(output_rows) > 0:
            utils.write_rows_to_csv(output_rows, output_csv, mode="a")


def _dedupe(output_csv):
    df = pd.read_csv(output_csv, keep_default_na=False)
    df.drop_duplicates(inplace=True, keep="first")
    df.to_csv(output_csv, index=False)
    return output_csv


if __name__ == "__main__":
    scrape()
