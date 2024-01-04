import logging
import re
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212", "palewire", "jsvine"]
__tags__ = ["historical", "excel", "pdf"]
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

    # Get data from the historical PDFs
    pdf_row_list = _get_historical_pdf_data(cache)

    # Set the export path
    data_path = data_dir / "ny.csv"

    # Combine and write out the file
    fieldnames = (
        list(html_row_list[0].keys())
        + list(excel_row_list[0].keys())
        + list(pdf_row_list[0].keys())
    )
    row_list = html_row_list + excel_row_list + pdf_row_list
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
        d = dict(
            company_name=td_list[0].a.text,
            notice_url=td_list[0].a["href"],
            date_posted=td_list[1].text,
            notice_dated=td_list[2].text,
        )
        row_list.append(d)
    return row_list


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


def _get_historical_pdf_data(cache):
    # See https://github.com/biglocalnews/warn-scraper/issues/476
    urls = (
        "https://github.com/biglocalnews/warn-scraper/files/8400324/FL-22-0165.Records.for.Release_Part1.pdf",
        "https://github.com/biglocalnews/warn-scraper/files/8400325/FL-22-0165.Records.for.Release_Part2.pdf",
        "https://github.com/biglocalnews/warn-scraper/files/8400326/FL-22-0165.Records.for.Release_Part3.pdf",
    )

    # Fetch the given file from its URL or the cache, return the local path
    def get_file(url):
        filename = url.split("/")[-1]
        cache_key = f"ny/{filename}"
        if cache.exists(cache_key):
            logger.debug(f"Fetching {filename} from cache")
            return cache.path / cache_key
        else:
            logger.debug(f"Downloading {filename}")
            return cache.download(cache_key, url)

    # Normalize the whitespace (esp. newlines) in a list of strings
    def clean_row(strings):
        return [re.sub(r"\s+", " ", s) for s in strings]

    # For each row of the main table on each page, yield a header:value dict
    def gen_rows_from_pdf(pdf):
        logger.debug(f"Parsing {pdf.stream.name.split('/')[-1]} …")
        for page in pdf.pages:
            logger.debug(f"Page {page.page_number}")

            # In a few instances, the *literal* whitespace characters in the
            # PDF cause unwanted effects.. Removing them, and instead relying
            # only on character positions, produces slightly better output.
            # (E.g., "St. Lawrence" instead of "S t.  Lawrence".) Not entirely
            # necessary, though.
            prepared = page.filter(lambda obj: obj.get("text") != " ")

            table = prepared.extract_table({"text_x_tolerance": 1})
            table_clean = list(map(clean_row, table))

            # Let's make sure we have the table we expect
            assert table_clean[0][0] == "Company"

            for row in table_clean[1:]:
                yield dict(zip(table_clean[0], row))

    def parse(path):
        with pdfplumber.open(path) as pdf:
            return list(gen_rows_from_pdf(pdf))

    paths = list(map(get_file, urls))
    return [y for x in map(parse, paths) for y in x]


if __name__ == "__main__":
    scrape()
