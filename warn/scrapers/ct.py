import logging
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = [
    "zstumgoren",
    "Dilcia19",
    "stucka",
]
__tags__ = ["html"]
__source__ = {
    "name": "Connecticut Department of Labor",
    "url": "https://www.ctdol.state.ct.us/progsupt/bussrvce/warnreports/warnreports.htm",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Connecticut.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # We start in 2015
    current_year = datetime.now().year

    # Get the full range of years
    year_range = range(2015, current_year + 1)

    output_rows = []
    for year in year_range:
        url = f"https://www.ctdol.state.ct.us/progsupt/bussrvce/warnreports/warn{year}.htm"
        cache_key = f"ct/{year}.html"

        if cache.exists(cache_key) and year < current_year:
            html = cache.read(cache_key)
        else:
            r = utils.get_url(url)
            html = r.text
            cache.write(cache_key, html)

        # Parse out the table
        soup = BeautifulSoup(html, "html.parser")
        if year == 2016:
            table = soup.find_all("table", "style15")
        else:
            table = soup.find_all("table", "MsoNormalTable")

        # Parse out the data
        row_list = _scrape_table(table)

        # Add data to the big list
        output_rows.extend(row_list)

    # Tack headers on the top
    header_row = [
        "warn_date",
        "affected_company",
        "layoff_location",
        "number_workers",
        "layoff_date",
        "closing",
        "closing_date",
        "union",
        "union_address",
    ]
    row_list = [header_row] + output_rows

    # Set the export path
    data_path = data_dir / "ct.csv"

    # Write out to csv
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path
    return data_path


def _scrape_table(table) -> list:
    """Scrape the provided table.

    Returns: List of data rows.
    """
    row_list = []
    # loop over table to process each row, skipping the header
    for table_row in table[0].find_all("tr")[1:]:

        # Get all the cells
        table_cells = table_row.find_all("td")

        # if a row has more than 9 cells it is handled separately
        # the 2016 table has some cells with nested tags
        if len(table_cells) > 9:
            output_row = _problem_cells(table_cells)
            row_list.append(output_row)
            continue
        # if a row has less than 9 it is skipped because it is incomplete
        elif len(table_cells) < 9:
            continue

        # for the rest, loop over cells for each row
        output_row = []
        for table_cell in table_cells:
            cell = table_cell.text.strip()
            cell = " ".join(cell.split())
            output_row.append(cell)

        # test to see if the row is blank
        if not output_row:
            continue

        # Add row to the big list
        row_list.append(output_row)

    # Pass it back
    logger.debug(f"{len(row_list)} rows parsed")
    return row_list


def _problem_cells(table_cells):
    """Deal with problem rows in the 2016 table."""
    output_row = []
    for table_cell in table_cells:
        current_cell = table_cell.text.strip()
        current_cell = " ".join(current_cell.split())
        if table_cells.index(table_cell) == 0:
            output_row.append(current_cell)
        else:
            previous_index = table_cells.index(table_cell) - 1
            previous_cell = table_cells[previous_index].text.strip()
            previous_cell = " ".join(previous_cell.split())
            if current_cell == previous_cell:
                continue
            else:
                output_row.append(current_cell)
    return output_row


if __name__ == "__main__":
    scrape()
