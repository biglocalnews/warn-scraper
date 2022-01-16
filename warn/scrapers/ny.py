import typing
import logging
from pathlib import Path

import pandas as pd

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from New York.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # currently just scrapes a historical file rather than the NY website
    output_csv = data_dir / "ny.csv"
    output_df = _scrape_historical(cache_dir)
    output_csv = output_df.to_csv(output_csv, index=False)
    return output_csv


def _scrape_historical(cache_dir):
    # download the historical data from the cloud
    data_url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/ny_historical.xlsx"
    )
    cache_key_historical = Path(cache_dir, "ny")
    cache_key_historical.mkdir(parents=True, exist_ok=True)
    cache_key_historical = f"{cache_key_historical}/historical.xlsx"
    historical_df = pd.DataFrame()
    try:
        logger.debug(f"Trying to read file {cache_key_historical} from cache...")
        historical_df = pd.read_excel(cache_key_historical, engine="openpyxl")
    except FileNotFoundError:
        logger.debug(
            f"Historical file not found in cache. Downloading to cache from {data_url}..."
        )
        utils.download_file(data_url, cache_key_historical)
        historical_df = pd.read_excel(cache_key_historical, engine="openpyxl")
    return historical_df


if __name__ == "__main__":
    scrape()
