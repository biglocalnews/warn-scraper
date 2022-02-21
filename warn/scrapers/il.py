import logging
import os
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html", "excel"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Illinois.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get the root page
    base_url = "https://www.illinoisworknet.com"
    index_url = f"{base_url}/LayoffRecovery/Pages/ArchivedWARNReports.aspx"
    page = utils.get_url(index_url)
    html = page.text

    # Save it to the cache
    state_code = "il"
    cache = Cache(cache_dir)
    cache.write(f"{state_code}/ArchivedWARNReports.html", html)

    # Parse out the list of links
    document = BeautifulSoup(html, "html.parser")
    table = document.find_all("table")[0]
    link_list = table.find_all("a")

    # Loop through the links
    output_rows = []
    current_year = datetime.now().year
    for link in link_list:
        href = link.get("href")
        if href is not None and href.startswith("/DownloadPrint"):
            # Decide whether to process based on the year in the file name
            file_name = urllib.parse.unquote(os.path.basename(href))
            year = _extract_year(file_name)
            first_year = 2004  # We don't currently support PDFs from years before this
            if year is not None and year >= first_year:
                # Download the file or provide the cache location
                cache_key = f"{state_code}/{file_name}"
                if cache.exists(cache_key) and year < current_year - 1:
                    file_path = cache_dir / cache_key
                else:
                    report_url = f"{base_url}{href}"
                    file_path = cache.download(cache_key, report_url)

                logger.debug(f"Processing {file_name}")

                # Parse the file
                if str(file_path).lower().endswith(".pdf"):
                    continue  # TODO: Implement PDF parsing
                elif str(file_path).lower().endswith(".xlsx"):
                    output_rows.extend(_parse_xlsx(file_path))

    # Get the headers from the last row
    headers = set().union(*(row.keys() for row in output_rows))

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"
    utils.write_dict_rows_to_csv(data_path, headers, output_rows)

    # Return the path to the CSV
    return data_path


def _parse_xlsx(xlsx_path: Path) -> list:
    """
    Parse XLSX tables.

    Keyword arguments:
    xlsx_path -- the Path to the XLSX

    Returns: a list of dicts that represent rows
    """
    output_rows = []

    workbook = load_workbook(filename=xlsx_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    for row in worksheet.rows:
        if row[0].value == "COMPANY NAME:":
            header_row = [cell.value for cell in row]
        elif row[0].value is not None:
            output_row = {
                _clean_column_name(header_row[col_index]): cell.value
                for col_index, cell in enumerate(row)
                if header_row[col_index] is not None
                and header_row[col_index] != "Column1"
            }

            output_rows.append(output_row)

    return output_rows


def _clean_column_name(name: str) -> str:
    """
    Merge columns with similar names.

    Keyword arguments:
    name -- the column name

    Returns: the cleaned column name
    """
    name = name.replace(":", "").strip()

    if name == "TELEPHONE":
        return "PHONE"
    if name == "REGION NUMBER & NAME" or name == "REGION NUMBER":
        return "REGION"
    if name == "Permanent or Temporary":
        return "TYPE OF LAYOFF"
    if name == "# WORKERS AFFECTED" or name == "ADDITIONAL WORKERS AFFECTED":
        return "WORKERS AFFECTED"
    if name == "WARN NOTIFIED DATE" or name == "WARN RECEIVED DATE":
        return "NOTICE DATE"

    return name


def _extract_year(text: str) -> Optional[int]:
    """
    Extract the year from a string.

    Keyword arguments:
    text -- the string to extract the year from

    Returns: the year
    """
    match = re.search(r"\d{4}", text)

    if match is not None:
        return int(match.group(0))

    return None


if __name__ == "__main__":
    scrape()
