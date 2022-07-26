import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import pdfplumber
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212"]
__tags__ = ["html", "pdf", "excel"]
__source__ = {
    "name": "California Employment Development Department",
    "url": "https://edd.ca.gov/en/Jobs_and_Training/Layoff_Services_WARN",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from California.

    Compiles a single CSV for CA using historical PDFs and an Excel file for the current fiscal year.

    Only regenerates the CSV if a PDF or the Excel file have changed.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)
    base_url = "https://edd.ca.gov/Jobs_and_Training"

    # Get the page with the link list
    logger.debug("Scraping list of data files")
    list_url = f"{base_url}/Layoff_Services_WARN.htm"
    list_page = utils.get_url(list_url)
    list_html = list_page.text
    cache.write("ca/list.html", list_html)

    # Parse out all the links
    list_soup = BeautifulSoup(list_html, "html.parser")
    link_list = []
    for link in list_soup.find_all("a"):
        # Grab the URL
        href_url = link.attrs.get("href", "").strip()

        # If it's a WARN link ...
        if re.search(r"warn[-_]?report", href_url, re.I):

            # Build it up
            if href_url.startswith("/"):
                full_url = f"https://edd.ca.gov{href_url}"
            else:
                full_url = href_url

            # Add it to the list
            link_list.append(full_url)

    # Download all the data files
    file_list = []
    for link in link_list:
        file_name = os.path.basename(urlparse(link).path)
        file_path = cache.download(f"ca/{file_name}", link)
        file_list.append(file_path)

    # Parse all the data files
    output_rows = []
    for file_ in file_list:
        if str(file_).endswith("pdf"):
            row_list = _extract_pdf_data(file_)
        else:
            row_list = _extract_excel_data(file_)
        output_rows += row_list

    # Write it out
    output_headers = [
        "notice_date",
        "effective_date",
        "received_date",
        "company",
        "city",
        "num_employees",
        "layoff_or_closure",
        "county",
        "address",
        "source_file",
    ]
    output_path = data_dir / "ca.csv"
    utils.write_dict_rows_to_csv(
        output_path, output_headers, output_rows, extrasaction="ignore"
    )

    # Return the path
    return output_path


def _extract_excel_data(wb_path):
    """Parse data from the provided Excel file."""
    logger.debug(f"Reading in {wb_path}")
    wb = load_workbook(filename=wb_path)
    # Get the only worksheet
    ws = wb.worksheets[0]
    rows = [row for row in ws.rows]
    # Throw away initial rows until we reach first data row
    while True:
        row = rows.pop(0)
        first_cell = row[0].value.strip().lower()
        if first_cell.startswith("county"):
            # Grab the header
            headers = row
            break

    # Get the location of the final two fields, which vary from week to week
    num_employees_index = next(
        i for i, c in enumerate(headers) if c.value and "employees" in c.value.lower()
    )
    address_index = next(
        i for i, c in enumerate(headers) if c.value and "address" in c.value.lower()
    )

    # Loop through all the rows
    payload = []
    for row in rows:
        first_cell = row[0].value.strip().lower()
        # Exit if we've reached summary row at bottom
        if first_cell == "report summary":
            break
        # Spreadsheet contains merged cells so index
        # positions below are not sequential
        data = {
            "county": row[0].value.strip(),
            "notice_date": _convert_date(row[1].value),
            "received_date": _convert_date(row[2].value),
            "effective_date": _convert_date(row[4].value),
            "company": row[5].value.strip(),
            "layoff_or_closure": row[8].value.strip(),
            "num_employees": row[num_employees_index].value,
            "address": row[address_index].value.strip(),
            "source_file": str(wb_path).split("/")[-1],
        }
        payload.append(data)
    return payload


def _convert_date(dt):
    return dt.strftime("%m/%d/%Y")


def _extract_pdf_data(pdf_path):
    headers = [
        "notice_date",
        "effective_date",
        "received_date",
        "company",
        "location",
        "city",
        "county",
        "num_employees",
        "layoff_or_closure",
        "source_file",
    ]
    header_crosswalk = {
        "Address": "location",
        "City": "city",
        "Company": "company",
        "County": "county",
        "Effective\nDate": "effective_date",
        "Effective \nDate": "effective_date",
        "Effective  \nDate": "effective_date",
        "Effective Date": "effective_date",
        "Employees": "num_employees",
        "Layoff/Closure": "layoff_or_closure",
        "Layoff/Closure Type": "layoff_or_closure",
        "No. Of \nEmployees": "num_employees",
        "No. Of Employees": "num_employees",
        "Notice\nDate": "notice_date",
        "Notice Date": "notice_date",
        "Received\nDate": "received_date",
        "Received \nDate": "received_date",
        "Received Date": "received_date",
    }
    data = []
    logger.debug(f"Opening {pdf_path} for PDF parsing")
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            # All pages pages except last should have a single table
            # Last page has an extra summary table, but indexing
            # for the first should avoid grabbing the summary data
            rows = page.extract_tables()[0]
            # Remove header row on first page
            # and update the standardized "headers" var if the source
            # data has no county field, as in the case of
            # files covering 07/2016-to-06/2017 fiscal year and earlier
            if idx == 0:
                raw_header = rows.pop(0)
                raw_header_str = "-".join([col.strip().lower() for col in raw_header])
                if "county" not in raw_header_str:
                    headers.remove("county")
            # Skip if it's a summary table (this happens
            # when summary is only table on page, as in 7/2019-6/2020)
            first_cell = rows[0][0].strip().lower()
            if "summary" in first_cell:
                continue
            for row in rows:
                data_row = {}
                for i, value in enumerate(row):
                    this_raw_header = raw_header[i]
                    this_clean_header = header_crosswalk[this_raw_header]
                    data_row[this_clean_header] = value
                # Data clean-ups
                data_row.update(
                    {
                        "effective_date": data_row["effective_date"].replace(" ", ""),
                        "received_date": data_row["received_date"].replace(" ", ""),
                        "source_file": str(pdf_path).split("/")[-1],
                    }
                )
                data.append(data_row)
    return data


if __name__ == "__main__":
    scrape()
