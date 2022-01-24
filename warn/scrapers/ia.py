import logging
from pathlib import Path

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly", "palewire"]
__tags__ = ["html", "excel"]

logger = logging.getLogger(__name__)


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
    row_list = []
    for r in worksheet.rows:
        column = [cell.value for cell in r]
        row_list.append(column)

    # Set the export path
    data_path = data_dir / "ia.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
