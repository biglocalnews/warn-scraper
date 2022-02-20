import logging
from datetime import datetime
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
    Scrape data from Ohio.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # Get years
    first_year = 2020  # First year of HTML data (prior years are PDFs)
    current_year = datetime.now().year
    years = range(first_year, current_year + 1)

    row_list = []

    # Loop through years
    base_url = "https://jfs.ohio.gov/warn/"
    for i, year in enumerate(years):
        if year == current_year:
            url = f"{base_url}current.stm"
        else:
            url = f"{base_url}archive.stm?year={year}"

        # Get the HTML
        r = utils.get_url(url)
        html = r.text
        cache.write(f"oh/{year}.html", html)

        # Parse the table
        row_list.extend(_parse_table(html, i > 0))

    # Write out
    data_path = data_dir / "oh.csv"
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the CSV
    return data_path


def _parse_table(html, skip_header) -> list:
    # Parse table
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all("table")

    # We expect the first table to be there with our data
    assert len(table_list) > 0
    table = table_list[1]

    # Parse the cells
    row_list = []
    for i, row in enumerate(table.find_all("tr")):
        if i == 0 and skip_header:
            continue
        cell_list = row.find_all(["th", "td"])
        if not cell_list:
            continue
        cell_list = [c.text.strip() for c in cell_list]
        row_list.append(cell_list)

    # Return it
    return row_list


if __name__ == "__main__":
    scrape()
