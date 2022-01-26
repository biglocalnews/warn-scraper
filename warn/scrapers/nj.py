import itertools
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = ["html"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from New Jersey.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Fire up the cache
    cache = Cache(cache_dir)

    # Get the root URL
    url = "http://lwd.state.nj.us/WorkForceDirectory/warn.jsp"
    r = utils.get_url(url)
    r.encoding = "utf-8"
    html = r.text

    # Cache the result
    cache.write("nj/source.html", html)

    # Parse out the tables
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all("table")

    # Each row is its own table. Yes, I know.
    output_rows = []
    for table in table_list:
        cell_list = [c.text.strip() for c in table.find_all("td")]
        output_rows.append(cell_list)

    # Get historical data from separate source
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
        # Get the HTML, trying the cache first
        if cache.exists(cache_key):
            html = cache.read(cache_key)
        else:
            # If file not found in cache, scrape the page and save to cache
            url = f"https://www.nj.gov/labor/lwdhome/warn/{year}/{html_page_name}"
            r = utils.get_url(url)
            r.encoding = "utf-8"
            html = r.text
            cache.write(cache_key, html)

        # Parse out the tables
        soup = BeautifulSoup(html, "html5lib")
        table_list = soup.find_all("table")
        table = table_list[0]

        # Loop through the rows
        for i, row in enumerate(table.find_all("tr")):

            # Skip the header row
            if i == 0:
                continue

            # Parse the data
            cell_list = [c.text.strip() for c in row.find_all("td")]

            # Add it to the pile
            output_rows.append(cell_list)

    # Set the export path
    data_path = data_dir / "nj.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
