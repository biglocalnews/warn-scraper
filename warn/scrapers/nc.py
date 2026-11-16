import logging
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["sanketdofe"]
__tags__ = ["html"]
__source__ = {
    "name": "North Carolina Department of Commerce",
    "url": "https://www.commerce.nc.gov/data-tools-reports/labor-market-data-tools/workforce-warn-reports",
}

logger = logging.getLogger(__name__)

# The columns we count on. The state can add more; they are kept as published.
EXPECTED_HEADERS = [
    "County",
    "Warn Number",
    "Date of Notice",
    "Date Received by NC",
    "Effective Date",
    "WARN Notice: WARN Notice Name",
    "WARN notice type",
    "Type of layoff or closure",
    "Number affected at this location",
    "Address 1",
    "City",
]


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from North Carolina.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # The state publishes one summary list per calendar year.
    # Only the current year is an HTML table; earlier years are PDFs.
    year = datetime.now().year
    url = f"{__source__['url']}/report-workforce-warn-summary-list-{year}"
    r = utils.get_url(url)
    html = r.text

    # Save it to the cache
    cache = Cache(cache_dir)
    cache.write(f"nc/{year}.html", html)

    # Parse the table, header first
    row_list = parse_table(html)

    # Set the export path
    data_path = data_dir / "nc.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the file
    return data_path


def parse_table(html: str) -> list[list[str]]:
    """
    Parse the summary list page into rows, with the header in the first row.

    Arguments:
    html -- the HTML of a year's "Workforce WARN Summary List" page

    Returns: a list of rows, each a list of cell strings
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find the notice table by its header, not by position or CSS class
    for table in soup.find_all("table"):
        headers = [_clean(th) for th in table.find_all("th")]
        if "Warn Number" in headers:
            break
    else:
        raise ValueError("North Carolina: no WARN notice table found on the page")

    missing = [h for h in EXPECTED_HEADERS if h not in headers]
    if missing:
        raise ValueError(
            f"North Carolina: table is missing expected columns {missing}; found {headers}"
        )

    row_list = [headers]
    for tr in table.find_all("tr"):
        cells = [_clean(td) for td in tr.find_all("td")]
        if not any(cells):
            continue
        if len(cells) != len(headers):
            raise ValueError(
                f"North Carolina: row has {len(cells)} cells, expected {len(headers)}: {cells}"
            )
        row_list.append(cells)

    if len(row_list) == 1:
        raise ValueError("North Carolina: the WARN notice table has no rows")

    logger.debug(f"Parsed {len(row_list) - 1} notices")
    return row_list


def _clean(cell) -> str:
    """Return a cell's text with runs of whitespace collapsed."""
    return " ".join(cell.get_text().split())


if __name__ == "__main__":
    scrape()
