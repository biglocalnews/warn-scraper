import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = ["html"]
__source__ = {
    "name": "Indiana Department of Workforce Development",
    "url": "https://www.in.gov/dwd/warn-notices/current-warn-notices/",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Indiana.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # Get the HTML
    latest_url = "https://www.in.gov/dwd/warn-notices/current-warn-notices/"
    r = utils.get_url(latest_url)
    latest_html = r.text
    cache.write("in/latest.html", latest_html)

    # Parse tables
    latest_soup = BeautifulSoup(latest_html, "html.parser")
    latest_tables = latest_soup.find_all("table")

    # Scrape table
    output_rows = []
    for i, table in enumerate(latest_tables):
        row_list = _parse_table(table, include_headers=i == 0)
        logger.debug(f"Scraped {len(row_list)} rows latest table {i+1}")
        output_rows.extend(row_list)

    # Write out
    data_path = data_dir / "in.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the CSV
    return data_path


def _parse_table(table, include_headers) -> list:
    # Parse the cells
    row_list = []
    tags = [
        "td",
    ]
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
