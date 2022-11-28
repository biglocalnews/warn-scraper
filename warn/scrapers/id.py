import logging
import random
import re
from pathlib import Path

import pdfplumber

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["pdf"]
__source__ = {
    "name": "Idaho Department of Labor",
    "url": "https://www.labor.idaho.gov/dnn/Businesses/Layoff-Assistance#2",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Idaho.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Create the URL of the source PDF
    base_url = "https://www.labor.idaho.gov/dnn/Portals/0/Publications/"
    file_name = "WARNNotice.pdf"
    # There's a numeric parameter called v on this PDF URL that updates
    # from time to time. Suspect this is a cache-buster. We're using a
    # random number instead.
    min_cache_buster = 0
    max_cache_buster = 10000000000
    cache_buster = random.randrange(min_cache_buster, max_cache_buster)
    url = f"{base_url}{file_name}?v={cache_buster}"

    # Download the PDF with verify=False because
    # there's a persistent cert error we're working around.
    cache = Cache(cache_dir)
    state_code = "id"
    cache_key = f"{state_code}/{file_name}"
    pdf_file = cache.download(cache_key, url, verify=False)

    # Loop through the PDF pages and scrape out the data
    output_rows: list = []
    with pdfplumber.open(pdf_file) as pdf:
        for index, page in enumerate(pdf.pages):
            rows = page.extract_table()
            output_rows += _clean_table(rows, index)

    # Write out the data to a CSV
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the CSV
    return data_path


def _clean_table(rows, page_index) -> list:
    """
    Clean up a table from a PDF.

    Keyword arguments:
    rows -- the rows of the table
    page_index -- the index of the page

    Returns: a list of lists, where each inner list is a row in the table
    """
    output_rows: list = []

    for row_index, row in enumerate(rows):
        output_row = []
        for col_index, column in enumerate(row):
            clean_text = _clean_text(column)

            # If cell is empty, copy from the cell above it
            # to deal with merged cells. Except for number of employees,
            # which is effectively a total for all locations in the merged cell
            # and which we don't want a data user to double count.
            if (
                _is_empty(clean_text)
                and _column_exists_in_prior_row(output_rows, row_index, col_index)
                and "No. of Employees"
                not in _column_name_from_index(output_rows, col_index)
            ):
                clean_text = output_rows[row_index - 1][col_index]

            output_row.append(clean_text)

        output_rows.append(output_row)

    # Only include the header on the first page
    if page_index != 0:
        return output_rows[1:]

    return output_rows


def _is_empty(text: str) -> bool:
    """
    Determine if a cell is empty.

    Keyword arguments:
    text -- the text to check

    Returns: True if the cell is empty, False otherwise
    """
    return text == ""


def _column_exists_in_prior_row(
    output_rows: list, row_index: int, col_index: int
) -> bool:
    """
    Determine if a column exists in the prior row.

    Keyword arguments:
    row_index -- the index of the row
    col_index -- the index of the column
    output_rows -- the output rows

    Returns: True if the column exists, False otherwise
    """
    return row_index > 0 and col_index < len(output_rows[row_index - 1])


def _column_name_from_index(output_rows: list, col_index: int) -> str:
    """
    Determine the column name from the column index.

    Keyword arguments:
    col_index -- the index of the column
    output_rows -- the output rows

    Returns: the column name
    """
    return output_rows[0][col_index]


def _clean_text(text: str) -> str:
    """
    Clean up text from a PDF cell.

    Keyword arguments:
    text -- the text to clean

    Returns: the cleaned text
    """
    if text is None:
        return ""
    # Collapse newlines
    partial = re.sub(r"\n", " ", text)
    # Standardize whitespace
    return re.sub(r"\s+", " ", partial)


if __name__ == "__main__":
    scrape()
