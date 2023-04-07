import logging
from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212", "palewire"]
__tags__ = ["historical", "excel"]
__source__ = {
    "name": "New York Department of Labor",
    "url": "https://dol.ny.gov/warn-notices",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from New York.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)

    # Get the latest HTML page
    url_list = [
        dict(year=2023, url="https://dol.ny.gov/warn-notices"),
        dict(year=2022, url="https://dol.ny.gov/2022-warn-notices"),
        dict(year=2021, url="https://dol.ny.gov/warn-notices-2021"),
    ]

    # Loop through the urls and get the stuff
    html_row_list = []
    for config in url_list:
        html_row_list += _get_html_data(cache, config)

    # Get the historical static data file
    excel_row_list = _get_historical_data(cache)

    # Set the export path
    data_path = data_dir / "ny.csv"

    # Combine and write out the file
    fieldnames = list(html_row_list[0].keys()) + list(excel_row_list[0].keys())
    row_list = html_row_list + excel_row_list
    utils.write_dict_rows_to_csv(
        data_path,
        fieldnames,
        row_list,
        extrasaction="ignore",
    )

    # Return the path to the file
    return data_path


def _get_html_data(cache, config):
    r = utils.get_url(config["url"])
    html = r.text

    # Save it to the cache
    cache.write(f"ny/{config['year']}.html", html)

    # Parse the HTML and grab our table
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("div", class_="landing-paragraphs").find("table")

    row_list = []
    # Loop through the rows of the table
    for tr in table.find_all("tr")[1:]:
        td_list = tr.find_all("td")
        notice_file_name = td_list[0].a["href"].strip()
        d = dict(
            company_name=td_list[0].a.text,
            notice_url=notice_file_name,
            date_posted=td_list[1].text,
            notice_dated=td_list[2].text,
        )
        # Crawl the indiviaual WARN notice PDFs to get addictional fields if possible
        d.update(_get_values_from_notice(notice_file_name, cache))
        row_list.append(d)
    return row_list


def _get_values_from_notice(notice_file_name: str, cache):
    details = dict(
        number_of_employees_affected=None, total_employees=None, event_number=None
    )
    tld = "https://dol.ny.gov"
    # Sometimes the notice_url is a full URL, sometimes it's just a path
    notice_url = (
        notice_file_name if notice_file_name.startswith(tld) else tld + notice_file_name
    )
    file_location = f"ny/{notice_file_name}.pdf"
    # Grab the PDF with the detailed data
    try:
        pdf_file = cache.download(file_location, notice_url)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting NY warn notice {notice_url}: {e}")
        return details
    with pdfplumber.open(pdf_file) as pdf:
        first_page = pdf.pages[0]
        n_affected_employees_match = first_page.search(
            r"(?<=Number Affected:)\s*[0-9,]+"
        )
        n_total_employees_match = first_page.search(r"(?<=Total Employees:)\s*[0-9,]+")
        event_number_match = first_page.search(r"(?<=Event Number:)\s*[0-9-]+")
        details["number_of_employees_affected"] = _regex_match_to_int(
            n_affected_employees_match
        )
        details["total_employees"] = _regex_match_to_int(n_total_employees_match)
        details["event_number"] = _get_first_regex_match(event_number_match)
    return details


def _get_first_regex_match(regex_match):
    if _is_valid_match(regex_match):
        return regex_match[0]["text"].strip()
    return None


def _regex_match_to_int(regex_match):
    first_match = _get_first_regex_match(regex_match)
    if first_match is not None:
        return int(first_match.replace(",", ""))
    return None


def _is_valid_match(regex_match):
    return bool(regex_match and len(regex_match) and regex_match[0])


def _get_historical_data(cache):
    # Request the page and save it to the cache
    url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/ny_historical.xlsx"
    )

    excel_path = cache.download("ny/source.xlsx", url)

    # Open it up
    workbook = load_workbook(filename=excel_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    # Convert the sheet to a list of lists
    row_list = []
    for r in worksheet.rows:
        column = [cell.value for cell in r]
        row_list.append(column)

    # Transform this into a list of dictionaries with headers as keys
    header_list = row_list.pop(0)
    dict_list = []
    for row in row_list:
        d = {}
        for i, cell in enumerate(row):
            key = header_list[i]
            # Skip any columns where the header is null
            if key is None:
                continue
            d[key] = cell
        dict_list.append(d)

    # Return the list of dicts
    return dict_list


if __name__ == "__main__":
    scrape()
