import logging
import random
import re
from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs", "stucka"]
__tags__ = ["pdf"]
__source__ = {
    "name": "Idaho Department of Labor",
    "url": "https://www.labor.idaho.gov/businesss/layoff-assistance/",
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
    base_url = "https://www.labor.idaho.gov"
    start_url = "https://www.labor.idaho.gov/businesss/layoff-assistance/"
    file_name = "WARNNotice.pdf"
    # There's a numeric parameter called v on this PDF URL that updates
    # from time to time. Suspect this is a cache-buster. We're using a
    # random number instead.
    min_cache_buster = 0
    max_cache_buster = 10000000000
    cache_buster = random.randrange(min_cache_buster, max_cache_buster)
    page_url = f"{start_url}?v={cache_buster}"

    cache = Cache(cache_dir)
    state_code = "id"
    logger.debug(f"Trying to fetch page at {page_url}")
    r = requests.get(page_url)

    # Start finding the link before "Who to contact"
    html = r.text
    localizedhtml = html.split("<h2>Who to contact")[0]
    soup = BeautifulSoup(localizedhtml, features="html5lib")
    last_url = soup.find_all("a")[-1]["href"]
    if "https" in last_url:
        pdf_url = last_url
    else:
        pdf_url = f"{base_url}{last_url}"

    logger.debug(f"Trying to fetch PDF at {pdf_url}")
    cache_key = f"{state_code}/{file_name}"
    pdf_file = cache.download(cache_key, pdf_url, verify=True)

    # Loop through the PDF pages and scrape out the data
    output_rows: list = []
    with pdfplumber.open(pdf_file) as pdf:
        for index, page in enumerate(pdf.pages):
            rows = page.extract_table()
            if rows[0][0] in ["Date of\nLetter", "Date of Letter"] and index > 1:
                rows = rows[
                    1:
                ]  # Drop inside header rows that _clean_table will mangle if merged cells span pages
            # logger.debug(f"\n\nRows for page {page}: {rows}")
            output_rows += _clean_table(rows, index)

    # Write out the data to a CSV
    data_path = data_dir / f"{state_code}.csv"
    output_rows = filter_garbage_rows(output_rows)
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
    #        if len(output_row) >= 3:
    #            output_rows.append(output_row)
    #        else:
    #            logger.debug(f"Dropping faulty row with {len(output_row)} elements: {output_row}")

    # Only include the header on the first page
    # No, this needed to be filtered earlier
    # if page_index != 0:
    #    return output_rows[1:]

    return output_rows


def filter_garbage_rows(incoming: list):
    """
    Return only rows with a minimum number of elements.

    Arguments: List of lists

    Returns: List of lists that have a minimum number of elements.
    """
    shortrows: int = 0
    mixedrows: int = 0
    outgoing: list = []
    for rowindex, row in enumerate(incoming):
        error = False
        if len(row) < 5:
            error = True
            logger.debug(f"Dropping short row: {row}")
            shortrows += 1
        if row[0] == "Date of Letter" and rowindex != 0:  # Keep the header row
            error = True
            logger.debug(f"Dropping partial row: {row}")
            mixedrows += 1
        if not error:
            outgoing.append(row)
    if shortrows == 0 and mixedrows == 0:
        logger.debug("No bad rows found.")
    else:
        logger.debug(
            f"!!!! Dropped {shortrows} rows with insufficient number of fields, and dropped {mixedrows} rows scrambled with header info"
        )
    return outgoing


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
