import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212"]
__tags__ = ["html"]
__source__ = {
    "name": "South Dakota Department of Labor and Regulation",
    "url": "https://dlr.sd.gov/workforce_services/businesses/warn_notices.aspx",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from South Dakota.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # Get the HTML
    url = "https://dlr.sd.gov/workforce_services/businesses/warn_notices.aspx"
    r = utils.get_url(url)
    html = r.text
    cache.write("sd/source.html", html)

    # Scrape out the data
    row_list = _parse_table(html)

    # Write out
    data_path = data_dir / "sd.csv"
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the CSV
    return data_path


def _parse_table(html) -> list:
    # Parse table
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all("table")

    # We expect the first table to be there with our data
    assert len(table_list) > 0
    table = table_list[0]

    # Parse the cells
    row_list = []
    for row in table.find_all("tr"):
        cell_list = []
        for cell in row.find_all(["th", "td"]):
            cell = re.sub(r"\s+", " ", cell.text.strip())
            cell_list.append(cell)
        if not cell_list:
            continue
        row_list.append(cell_list)

    # Return it
    return row_list


if __name__ == "__main__":
    scrape()
