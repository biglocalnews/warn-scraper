import logging
from pathlib import Path

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


if __name__ == "__main__":
    scrape()
