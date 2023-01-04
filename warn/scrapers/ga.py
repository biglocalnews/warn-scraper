import logging
import re
import time
import typing
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html"]
__source__ = {
    "name": "Georgia Department of Labor",
    "url": "https://www.dol.state.ga.us/public/es/warn/searchwarns/list",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Georgia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    state_code = "ga"
    cache = Cache(cache_dir)

    # The basic configuration for the scrape
    base_url = "http://www.dol.state.ga.us/public/es/warn/searchwarns/list"

    area = 9  # statewide

    current_year = datetime.now().year
    first_year = 1989  # first available year

    years = list(range(first_year, current_year + 1))
    years.reverse()

    # Loop through the years and scrape them one by one
    output_rows: typing.List = []
    for i, year in enumerate(years):
        # Concoct the URL
        url = f"{base_url}?geoArea={area}&year={year}&step=search"
        cache_key = f"{state_code}/{year}.html"

        # Read from cache if available and not this year or the year before
        if cache.exists(cache_key) and year < current_year - 1:
            html = cache.read(cache_key)
        else:
            # Otherwise, go request it
            page = utils.get_url(url, verify=False)
            html = page.text
            cache.write(cache_key, html)

        # Scrape out the table
        new_rows = _parse_table(
            html,
            "emplrList",
            include_headers=len(output_rows) == 0 or i == 0,  # After the first loop, we can skip the headers
        )

        # Concatenate the rows
        output_rows.extend(new_rows)

        # Sleep a bit
        time.sleep(2)

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the CSV
    return data_path


def _parse_table(html, id, include_headers=True) -> typing.List:
    """
    Parse HTML table with given ID.

    Keyword arguments:
    html -- the HTML to parse
    id -- the ID of the table to parse
    include_headers -- whether to include the headers in the output (default True)

    Returns: a list of rows
    """
    # Parse out data table
    soup = BeautifulSoup(html, "html5lib")
    table_list = soup.find_all(id=id)  # output is list-type

    # We expect the first table to be there with our data
    try:
        assert len(table_list) > 0
    except AssertionError:
        logger.debug("No tables found")
        return []
    table = table_list[0]

    output_rows = []
    column_tags = ["td"]

    if include_headers:
        column_tags.append("th")

    # Loop through the table and grab the data
    for table_row in table.find_all("tr"):
        columns = table_row.find_all(column_tags)
        output_row = []

        for column in columns:
            # Collapse newlines
            partial = re.sub(r"\n", " ", column.text)
            # Standardize whitespace
            clean_text = re.sub(r"\s+", " ", partial).strip()
            output_row.append(clean_text)

        # Skip any empty rows
        if len(output_row) == 0 or output_row == [""]:
            continue

        output_rows.append(output_row)

    return output_rows


if __name__ == "__main__":
    scrape()
