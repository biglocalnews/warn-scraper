import logging
import os
import re
import urllib.parse
from pathlib import Path
from typing import Optional

import pdfplumber
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html", "pdf", "xlsx"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Georgia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)

    state_code = "il"
    base_url = "https://www.illinoisworknet.com"
    first_year = 2004  # We don't currently support PDFs from years before this

    index_url = f"{base_url}/LayoffRecovery/Pages/ArchivedWARNReports.aspx"

    page = utils.get_url(index_url)
    html = page.text

    cache.write(f"{state_code}/ArchivedWARNReports.html", html)

    document = BeautifulSoup(html, "html.parser")
    table = document.find_all("table")[0]
    links = table.find_all("a")

    output_rows = []

    for link in links:
        href = link.get("href")
        if href is not None and href.startswith("/DownloadPrint"):
            report_url = f"{base_url}{href}"
            file_name = urllib.parse.unquote(os.path.basename(href))
            cache_key = f"{state_code}/{file_name}"
            if cache.exists(cache_key):
                file_path = Path(cache_dir, cache_key)
            else:
                file_path = cache.download(cache_key, report_url)

            logger.debug(f"Processing {file_name}")

            year = _extract_year(file_name)
            if (
                str(file_path).lower().endswith(".pdf")
                and year is not None
                and year >= first_year
            ):
                output_rows.extend(_parse_pdf(file_path))
            elif str(file_path).lower().endswith(".xlsx"):
                output_rows.extend(_parse_xlsx(file_path))

    headers = set().union(*(row.keys() for row in output_rows))

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"
    utils.write_dict_rows_to_csv(data_path, headers, output_rows)

    # Return the path to the CSV
    return data_path


def _parse_pdf(pdf_path: Path) -> list:
    """
    Parse PDF.

    Keyword arguments:
    pdf_path -- the Path to the PDF

    Returns: a list of dicts that represent rows
    """
    output_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            rows = _parse_pdf_tables(page)

            if len(rows) > 0:
                output_rows.extend(rows)
            else:
                rows = _parse_pdf_text(page)
                output_rows.extend(rows)

    return output_rows


def _parse_pdf_tables(page: pdfplumber.pdf.Page) -> list:
    """
    Parse PDF tables.

    Keyword arguments:
    page -- a PDF page

    Returns: a list of dicts that represent rows
    """
    output_rows = []

    tables = page.extract_tables()

    output_row = {}

    if len(tables) > 0:
        for table in tables:
            for row in table:
                for col_index, column in enumerate(row):
                    if (
                        column is not None
                        and column.endswith(":")
                        and col_index + 2 < len(row)
                    ):
                        col_name = _clean_column_name(column)
                        output_row[col_name] = row[col_index + 2]

            output_rows.append(output_row)

    return output_rows


def _parse_pdf_text(page: str) -> list:
    """
    Parse PDF text.

    Keyword arguments:
    page -- a PDF page

    Returns: a list of dicts that represent rows
    """
    pass

    # text = page.extract_text()

    # print(text)

    return []


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
        return "iNTIAL NOTICE DATE"

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
