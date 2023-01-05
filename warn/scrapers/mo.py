import logging
import re
import typing
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html"]
__source__ = {
    "name": "Missouri Office of Workforce Development",
    "url": "https://jobs.mo.gov/warn/",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Missouri.

    NOTES for data cleaning:
    - 2019 and 2020 page has duplicate data
    - 2017 date format is different

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # Get the range of years we're after
    today = datetime.today()
    current_year = today.year
    year_range = list(range(2019, current_year + 1))
    year_range.reverse()

    # Download them all
    html_list = []
    for year in year_range:

        # Set the URL, with a hack for 2020 and 2022
        url = f"https://jobs.mo.gov/warn/{year}"

        # Read from cache if available and not this year or the year before
        cache_key = f"mo/{year}.html"
        if cache.exists(cache_key) and year < current_year - 1:
            html = cache.read(cache_key)
        else:
            # Otherwise, go request it
            r = utils.get_url(url)
            html = r.text
            # Save it to the cache
            cache.write(cache_key, html)

        # Add it to the list
        html_list.append(html)

    # Parse them all
    logger.debug(f"{len(html_list)} pages downloaded")
    output_rows: typing.List = []
    for i, html in enumerate(html_list):
        logger.debug(f"Parsing page #{i+1}")
        soup = BeautifulSoup(html, "html5lib")

        # Pull out the table
        table_list = soup.find_all("table")
        try:
            assert len(table_list) > 0
        except AssertionError:
            logger.debug("No tables found")
            continue
        table = table_list[0]

        # Get all rows
        row_list = table.find_all("tr")

        # If it's not the first row, slice off the header
        if len(output_rows) > 0:
            row_list = row_list[1:]

        # Loop through all the rows
        year_rows = []
        for row in row_list:
            # Get the cells
            cell_list = row.find_all(["td", "th"])

            # Clean them up
            cell_list = [_clean_text(c.text) for c in cell_list]

            if len(cell_list) < 9:  # to account for the extra column in 2021
                cell_list.insert(2, "")

            # Pass them out
            year_rows.append(cell_list)

        # pop "Total" row
        year_rows.pop(len(year_rows) - 1)

        # Add to master list
        output_rows.extend(year_rows)

    # Set the export path
    data_path = data_dir / "mo.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


def _clean_text(text):
    """Clean up the provided HTML snippet."""
    if text is None:
        return ""
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


if __name__ == "__main__":
    scrape()
