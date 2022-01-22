import logging
import random
import re
from pathlib import Path

import pdfplumber
import requests

from .. import utils

__authors__ = ["chriszs"]
__tags__ = ["pdf"]

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
    state_code = "id"
    base_url = "https://www.labor.idaho.gov/dnn/Portals/0/Publications/"
    file_name = "WARNNotice.pdf"

    # There's a numeric parameter called v on this PDF URL that updates
    # from time to time. Suspect this is a cache-buster. We're using a
    # random number instead.
    min_cache_buster = 0
    max_cache_buster = 10000000000
    cache_buster = random.randrange(min_cache_buster, max_cache_buster)

    url = f"{base_url}{file_name}?v={cache_buster}"

    cache_state = Path(cache_dir, state_code)
    cache_state.mkdir(parents=True, exist_ok=True)

    cache_key = f"{cache_state}/WARNNotice.pdf"

    # verify=False because there's a persistent cert error
    # we're working around.
    response = requests.get(url, verify=False)
    with open(cache_key, "wb") as file:
        file.write(response.content)

    output_rows = []

    with pdfplumber.open(cache_key) as pdf:
        for index, page in enumerate(pdf.pages):
            rows = page.extract_table()

            output_rows = output_rows + _clean_table(rows, index)

    # Write out the data to a CSV
    data_path = Path(data_dir, f"{state_code}.csv")
    utils.write_rows_to_csv(output_rows, data_path)

    return data_path


def _clean_table(rows: list, page_index: int) -> list:
    """
    Clean up a table from a PDF.

    Keyword arguments:
    rows -- the rows of the table
    page_index -- the index of the page

    Returns: a list of lists, where each inner list is a row in the table
    """
    output_rows = []

    for row_index, row in enumerate(rows):
        output_row = []
        for col_index, column in enumerate(row):
            clean_text = _clean_text(column)

            # If cell is empty, copy from the cell above it
            # to deal with merged cells. Except for number of employees,
            # which is effectively a total for all locations in the merged cell
            # and which we don't want a data user to double count.
            if (
                clean_text == ""
                and row_index > 0
                and col_index < len(output_rows[row_index - 1])
                and output_rows[0][col_index] != "No. of Employees Affected"
            ):
                clean_text = output_rows[row_index - 1][col_index]

            output_row.append(clean_text)

        output_rows.append(output_row)

    # Only include the header on the first page
    if page_index != 0:
        return output_rows[1:]

    return output_rows


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
