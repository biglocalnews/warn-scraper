import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["Dilcia19", "ydoc5212"]
__tags__ = ["html", "excel", "historical"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Texas.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)

    url = "https://www.twc.texas.gov/businesses/worker-adjustment-and-retraining-notification-warn-notices#warnNotices"
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")

    # download each year's excel file
    links = soup.find_all("a", href=re.compile("^/files/news/warn-act-listings-"))

    row_list = []
    for link in links:
        link_url = link.get("href")
        filename_regex = re.match(r".*-(.{4})(\..*)$", link_url, re.I)
        year = int(filename_regex.group(1)[-4:])  # extract year as integer
        # only scrape after year 2019 since our historical document covers 2018 and before
        # (the historical doc includes 2019 too but the year seems to be missing some entries)
        if year >= 2019:
            file_extension = filename_regex.group(
                2
            )  # extract extension string (eg .xls, .xlsx)

            # get each url from the HTML links we found
            data_url = f'https://www.twc.texas.gov{link.get("href")}'

            # download the excel file
            excel_path = cache.download(f"tx/{year}{file_extension}", data_url)

            # Open it up
            workbook = load_workbook(filename=excel_path)

            # Get the first sheet
            worksheet = workbook.worksheets[0]

            # Convert the sheet to a list of lists
            for r in worksheet.rows:
                column = [cell.value for cell in r]
                # Skip empty rows
                if column[0] is None:
                    continue
                row_list.append(column)

    # Get historical URL
    historical_url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/tx_historical.xlsx"
    )
    excel_path = cache.download("tx/historical.xlsx", historical_url)

    # Open it up
    workbook = load_workbook(filename=excel_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    # Convert the sheet to a list of lists
    for r in worksheet.rows:
        column = [cell.value for cell in r]
        row_list.append(column)

    # Set the export path
    data_path = data_dir / "tx.csv"

    # Write out the file
    utils.write_rows_to_csv(row_list, data_path)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
