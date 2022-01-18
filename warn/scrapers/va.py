import typing
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Virginia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "va.csv"
    url = "https://www.vec.virginia.gov/warn-notices"
    response = utils.get_url(url)
    soup = BeautifulSoup(response.text, "html.parser")
    data_url = soup.find("a", text="Download")["href"]
    data_url = f"https://www.vec.virginia.gov{data_url}"
    utils.download_file(data_url, output_csv)
    return output_csv


if __name__ == "__main__":
    scrape()
