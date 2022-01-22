import os
import re
from datetime import datetime
from pathlib import Path
import urllib.parse

from bs4 import BeautifulSoup
import pdfplumber
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html"]


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

    index_url = f"{base_url}/LayoffRecovery/Pages/ArchivedWARNReports.aspx"

    page = utils.get_url(index_url)
    html = page.text

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")

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

            if str(file_path).lower().endswith(".pdf"):
                _parse_pdf_tables(file_path)
            elif str(file_path).lower().endswith(".xlsx"):
                _parse_xlsx_tables(file_path)

            output_rows.append([file_path])

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(output_rows, data_path)

    # Return the path to the CSV
    return data_path


def _parse_pdf_tables(pdf_path: Path) -> list:
    """
    Parse PDF tables.

    Keyword arguments:
    pdf_path -- the Path to the PDF

    Returns: a list of lists of strings
    """
    output_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages):
            rows = page.extract_tables()

            print(rows)

    return output_rows

def _parse_xlsx_tables(xlsx_path: Path) -> list:
    """
    Parse XLSX tables.

    Keyword arguments:
    xlsx_path -- the Path to the XLSX

    Returns: a list of lists of strings
    """
    output_rows = []

    workbook = load_workbook(filename=xlsx_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    for row in worksheet.rows:
        if not all(cell.value is None for cell in row):
            print([cell.value for cell in row])

    return output_rows

if __name__ == "__main__":
    scrape()
