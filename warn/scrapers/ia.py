import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly", "palewire"]
__tags__ = ["html", "excel"]
__source__ = {
    "name": "Iowa Workforce Development Department",
    "url": "https://www.iowaworkforcedevelopment.gov/worker-adjustment-and-retraining-notification-act",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Iowa.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Go to the page
    url = "https://www.iowaworkforcedevelopment.gov/worker-adjustment-and-retraining-notification-act"
    r = utils.get_url(url)
    html = r.text

    # Save it to the cache
    cache = Cache(cache_dir)
    cache.write("ia/source.html", html)

    # Parse out the Excel link
    soup = BeautifulSoup(html, "html.parser")
    excel_url = soup.find("a", {"title": "WARN Log Excel File"})["href"]
    if not excel_url.startswith("http"):
        excel_url = "https://www.iowaworkforcedevelopment.gov" + excel_url

    # Download the Excel file
    excel_path = cache.download("ia/source.xlsx", excel_url)

    # Parse it
    row_list = utils.parse_excel(excel_path)

    # Get historic file
    historic_url = "https://www.iowaworkforcedevelopment.gov/sites/search.iowaworkforcedevelopment.gov/files/documents/2018/WARN_20180503.xlsx"
    historic_excel_path = cache.download("ia/historic.xlsx", historic_url)

    # Parse it, minus the header
    row_list += utils.parse_excel(historic_excel_path, keep_header=False)

    # Set the export path
    data_path = data_dir / "ia.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
