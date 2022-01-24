import logging
from pathlib import Path
from typing import Any

from attrs import define
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly", "palewire"]
__tags__ = ["html", "excel"]

logger = logging.getLogger(__name__)


@define(frozen=True)
class Notice:
    """A WARN notice posted by the state of Iowa."""

    company: Any = utils.rawfield("Company")
    address_line_1: Any = utils.rawfield("Address Line 1")
    city: Any = utils.rawfield("City")
    county: Any = utils.rawfield("County")
    st: Any = utils.rawfield("St")
    zip: Any = utils.rawfield("ZIP")
    notice_type: Any = utils.rawfield("Notice Type")
    emp_number: Any = utils.rawfield("Emp #")
    notice_date: Any = utils.rawfield("Notice Date")
    layoff_date: Any = utils.rawfield("Layoff Date")


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Iowa.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Go to the page
    url = "https://www.iowaworkforcedevelopment.gov/worker-adjustment-and-retraining-notification-act"
    r = utils.get_url(url)
    html = r.text

    # Save it to the cache
    cache = Cache(cache_dir)
    cache.write("ia/source.html", html)

    # Parse out the Excel link
    soup = BeautifulSoup(html, "html.parser")
    excel_url = soup.find("a", {"title": "WARN Log Excel File"})["href"]

    # Download the Excel file
    excel_path = cache.download("ia/source.xlsx", excel_url)

    # Open it up
    workbook = load_workbook(filename=excel_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    # Convert the sheet to a list of lists
    notice_list = []
    for i, r in enumerate(worksheet.rows):
        # Skip the header row
        if i == 0:
            continue

        # There is only data in first 10 columns
        column_list = r[:10]

        # Pull the values
        cell_list = [_clean_cell(cell.value) for cell in column_list]

        # Skip empty rows
        try:
            # A list with only empty cell will throw an error
            next(i for i in cell_list if i)
        except StopIteration:
            continue

        notice_obj = Notice(*cell_list)
        notice_list.append(notice_obj)

    # Set the export path
    data_path = data_dir / "ia.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the file
    return data_path


def _clean_cell(val):
    """Clean the provided cell and return it."""
    if isinstance(val, str):
        return val.strip()
    return val


if __name__ == "__main__":
    scrape()
