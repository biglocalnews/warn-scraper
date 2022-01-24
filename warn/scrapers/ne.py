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
    Scrape data from Nebraska.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    current_year = datetime.now().year
    year_range = range(2010, current_year + 1)

    # Scrape rows
    output_rows = []
    for year in year_range:
        # Get WARN page
        warn_url = (
            f"https://dol.nebraska.gov/LayoffServices/WARNReportData/?year={year}"
        )
        warn_key = f"ne/warn-{year}.html"

        # Read from cache if available and not this year or the year before
        if cache.exists(warn_key) and year < current_year - 1:
            warn_html = cache.read(warn_key)
        else:
            warn_r = utils.get_url(warn_url)
            warn_html = warn_r.text
            cache.write(warn_key, warn_html)

        # Parse the table
        warn_headers = ["Date", "Company", "Jobs Affected", "City", "Location"]
        warn_rows = _parse_table(warn_html, warn_headers)

        # Add it to the big list
        output_rows.extend(warn_rows)

        # Do the same for the layoffs page
        layoff_url = f"https://dol.nebraska.gov/LayoffServices/LayoffAndClosureReportData/?year={year}"
        layoff_key = f"ne/layoff-{year}.html"

        # Read from cache if available and not this year or the year before
        if cache.exists(layoff_key) and year < current_year - 1:
            layoff_html = cache.read(layoff_key)
        else:
            page = utils.get_url(layoff_url)
            layoff_html = page.text
            cache.write(layoff_key, layoff_html)

        # Parse the table
        layoff_headers = [
            "Date",
            "Company",
            "Type",
            "Jobs Affected",
            "City",
            "Location",
        ]
        layoff_rows = _parse_table(layoff_html, layoff_headers)

        # Add it to the big list
        output_rows.extend(layoff_rows)

    # Write out the results
    data_path = data_dir / "ne.csv"
    utils.write_dict_rows_to_csv(
        data_path, layoff_headers, output_rows, extrasaction="ignore"
    )

    # Return the path to the CSV
    return data_path


def _parse_table(html, headers) -> list:
    # Parse table
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all("table")

    # We expect the first table to be there with our data
    assert len(table_list) > 0
    table = table_list[0]

    # Parse the cells
    row_list = []
    for row in table.find_all("tr"):
        cell_list = row.find_all("td")
        if not cell_list:
            continue
        cell_dict = {headers[i]: c.text.strip() for i, c in enumerate(cell_list)}
        row_list.append(cell_dict)

    # Return it
    return row_list


if __name__ == "__main__":
    scrape()
