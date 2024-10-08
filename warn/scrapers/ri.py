import logging
import typing
from pathlib import Path

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212", "chriszs", "stucka"]
__tags__ = ["excel"]
__source__ = {
    "name": "Rhode Island Department of Labor and Training",
    "url": "https://dlt.ri.gov/employers/worker-adjustment-and-retraining-notification-warn",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Rhode Island.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    state_code = "ri"

    # Get the HTML
    base_url = "https://dlt.ri.gov/"
    url = f"{base_url}/employers/worker-adjustment-and-retraining-notification-warn"
    r = utils.get_url(url)
    html = r.text
    cache.write(f"{state_code}/source.html", html)

    # Find links
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")

    for link in links:
        if "WARN Report" in link.text:
            excel_url = f"{base_url}{link.get('href')}"
            excel_path = cache.download(f"{state_code}/WARN Report.xlsx", excel_url)

            # Open it up
            workbook = load_workbook(filename=excel_path)

            dirty_list: list = []
            for sheet in workbook.worksheets:
                localrows = parse_xlsx(sheet)
                dirty_list.extend(localrows)

            headers = dirty_list[1]  # Skip false header at position 0
            headers = [x for x in headers if x is not None]
            headers[2] = (
                headers[2]
                .replace("Company Name ", "Company Name")
                .replace(
                    "Company Name (* Denotes Covid 19 Related WARN)", "Company Name"
                )
            )
            row_list: list = []
            for rowindex, row in enumerate(dirty_list):
                if (
                    row != headers
                ):  # Filter out headers, but also double-check when headers may change
                    if row[0] and row[0] == "Rhode Island WARN Report":
                        continue
                    elif not row[2]:
                        logger.debug(f"Missing data for company name in row: {row}")
                    elif "Company Name" in row[2]:
                        logger.debug(
                            f"Dropping dirty row that doesn't quite match headers in row {rowindex}"
                        )
                        logger.debug(f"Want: {headers}")
                        logger.debug(f"Got : {row}")
                    else:
                        line = {}
                        if len(headers) > len(row):
                            logger.debug(
                                f"{len(row)} items found, vs. expected {len(headers)}. Dropping row: {row}"
                            )
                        else:
                            for i, fieldname in enumerate(headers):
                                line[fieldname] = row[i]
                            row_list.append(line)
            # dirty_list = None
            logger.debug(
                f"Successfully merged {len(row_list)-1:,} records from new spreadsheet."
            )

    # Write out
    data_path = data_dir / "ri.csv"
    utils.write_dict_rows_to_csv(data_path, headers, row_list, extrasaction="ignore")

    # Return the path to the CSV
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
