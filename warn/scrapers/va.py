import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html", "csv"]
__source__ = {
    "name": "Virginia Employment Commission",
    "url": "https://www.vec.virginia.gov/warn-notices",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Virginia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get the WARN page
    url = "https://www.vec.virginia.gov/warn-notices"
    r = utils.get_url(url)
    html = r.text

    # Save it to the cache
    cache = Cache(cache_dir)
    cache.write("va/source.html", html)

    # Parse out the CSV download link
    soup = BeautifulSoup(html, "html.parser")
    csv_href = soup.find("a", text="Download")["href"]
    csv_url = f"https://www.vec.virginia.gov{csv_href}"

    # Download it to the cache
    cache.download("va/source.csv", csv_url)

    # Open it up as a list of rows
    csv_rows = cache.read_csv("va/source.csv")

    # Set the export path
    data_path = data_dir / "va.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, csv_rows)

    # Return the export path
    return data_path


if __name__ == "__main__":
    scrape()
