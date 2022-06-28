import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = ["html"]
__source__ = {
    "name": "Utah Department of Workforce Services",
    "url": "https://jobs.utah.gov/employer/business/warnnotices.html",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Utah.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # Get the HTML
    url = "https://jobs.utah.gov/employer/business/warnnotices.html"
    r = utils.get_url(url)
    html = r.text
    cache.write("ut/source.html", html)

    # Parse table
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all("table")

    # Scrape out the data
    row_list = []
    for i, table in enumerate(table_list):
        row_list.extend(_parse_table(table, i == 0))

    # Write out
    data_path = data_dir / "ut.csv"
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the CSV
    return data_path


def _parse_table(table, include_headers) -> list:
    # Parse the cells
    row_list = []
    tags = ["td"]
    if include_headers:
        tags.append("th")
    for row in table.find_all("tr"):
        cell_list = row.find_all(tags)
        if not cell_list:
            continue
        cell_list = [c.text.strip() for c in cell_list]
        row_list.append(cell_list)

    # Return it
    return row_list


if __name__ == "__main__":
    scrape()
