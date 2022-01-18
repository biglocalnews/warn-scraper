import typing
import logging
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Iowa.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "ia.csv"
    url = "https://www.iowaworkforcedevelopment.gov/worker-adjustment-and-retraining-notification-act"
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")
    data_url = soup.find("a", {"title": "WARN Log Excel File"})["href"]
    df = pd.read_excel(data_url)
    df.dropna(inplace=True, axis=1, how="all")
    df.to_csv(output_csv, index=False)
    return output_csv


if __name__ == "__main__":
    scrape()
