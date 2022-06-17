import logging
from pathlib import Path

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212", "chriszs"]
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

    row_list = []

    for link in links:
        if "WARN Report" in link.text:
            excel_url = f"{base_url}{link.get('href')}"
            excel_path = cache.download(f"{state_code}/WARN Report.xlsx", excel_url)

            # Open it up
            workbook = load_workbook(filename=excel_path)

            # Get the first sheet
            worksheet = workbook.worksheets[0]

            for r in list(worksheet.rows)[3:]:
                column = [cell.value for cell in r]
                row_list.append(column)

    # Write out
    data_path = data_dir / "ri.csv"
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
