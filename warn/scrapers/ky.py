import csv
import logging
import typing
from pathlib import Path

import requests
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = [
    "palewire",
    "stucka",
]
__tags__ = [
    "excel",
]
__source__ = {
    "name": "Kentucky Career Center",
    "url": "https://kcc.ky.gov/employer/Pages/Business-Downsizing-Assistance---WARN.aspx",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Kentucky.

    Arguments:
    output_dir -- the Path were the result will be saved

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get the latest workbook
    cache = Cache(cache_dir)
    hostpage = "https://kcc.ky.gov/Pages/News.aspx"
    baseurl = "https://kcc.ky.gov"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0"
    }
    r = requests.get(hostpage, headers=headers)
    html = r.text
    subpage = html.split("WARN Notices by Year</h4")[-1]
    # mypy and BeautifulSoup are not cooperating. So ... extract the URL in a dumb way.
    fragment = subpage.split('href="')[1].split('"')[0]
    latest_url = f"{baseurl}{fragment}"

    # latest_url = "https://kcc.ky.gov/WARN%20notices/WARN%20NOTICES%202022/WARN%20Notice%20Report%2001262022.xls"
    latest_path = cache.download("ky/latest.xlsx", latest_url)

    # Open it up
    workbook = load_workbook(filename=latest_path)

    dirty_list: list = []
    for sheet in workbook.worksheets:
        localrows = parse_xlsx(sheet)
        dirty_list.extend(localrows)

    headers = dirty_list[0]
    row_list = []
    for rowindex, row in enumerate(dirty_list):
        if (
            row != headers
        ):  # Filter out headers, but also double-check when headers may change
            if row[0] == "Date Received":
                logger.debug(
                    f"Dropping dirty row that doesn't quite match headers in row {rowindex}"
                )
                logger.debug(f"Want: {headers}")
                logger.debug(f"Got : {row}")
            else:
                line = {}
                for i, fieldname in enumerate(headers):
                    line[fieldname] = row[i]
                row_list.append(line)
    # dirty_list = None
    logger.debug(
        f"Successfully merged {len(row_list)-1:,} records from new spreadsheet."
    )

    # Need to double-check this archived file code, and make sure headers match

    archive_url = "https://storage.googleapis.com/bln-data-public/warn-layoffs/ky-historical-normalized.csv"

    logger.debug("Getting KY historical data")
    r = requests.get(archive_url)

    reader = list(csv.reader(r.text.splitlines()))

    headerlength = len(headers)

    assert reader[0][:headerlength] == headers
    logger.debug(
        f"Historical data matches current headers. Merging {len(reader)-1:,} records."
    )

    for row in reader[1:]:  # Skip header row
        line = {}
        for i, item in enumerate(headers):
            line[item] = row[
                i
            ]  # Make this a list of dictionaries to match earlier input
        row_list.append(line)

    # Write out the results
    data_path = data_dir / "ky.csv"
    utils.write_dict_rows_to_csv(data_path, headers, row_list, extrasaction="ignore")

    # Pass it out
    return data_path


def parse_xlsx(worksheet) -> typing.List[typing.List]:
    """Parse the Excel xlsx file at the provided path.

    Args:
        worksheet: An openpyxl worksheet ready to parse

    Returns: List of values ready to write.
    """
    # Convert the sheet to a list of lists
    row_list = []
    for r in worksheet.rows:
        # Parse cells
        cell_list = [cell.value for cell in r]

        # Skip empty rows
        try:
            # A list with only empty cells will throw an error
            next(c for c in cell_list if c)
        except StopIteration:
            continue

        # Add to the master list
        row_list.append(cell_list)

    # Pass it back
    return row_list


if __name__ == "__main__":
    scrape()
