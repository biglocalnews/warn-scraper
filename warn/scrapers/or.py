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
    Scrape data from Oregon.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "or.csv"
    output_df = _scrape_historical(cache_dir)
    output_df.to_csv(output_csv, index=False)
    return output_csv


# download the historical data from the cloud
def _scrape_historical(cache_dir):
    data_url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/or_historical.xlsx"
    )
    cache_key_historical = Path(cache_dir, "or")
    cache_key_historical.mkdir(parents=True, exist_ok=True)
    cache_key_historical = f"{cache_key_historical}/historical.xlsx"
    historical_df = pd.DataFrame()
    # we skip the first 2 rows of the OR historical excel
    try:
        logger.debug(f"Trying to read file {cache_key_historical} from cache...")
        historical_df = pd.read_excel(
            cache_key_historical, skiprows=2, engine="openpyxl"
        )
    except FileNotFoundError:
        logger.debug(
            f"Historical file not found in cache. Downloading to cache from {data_url}..."
        )
        utils.download_file(data_url, cache_key_historical)
        historical_df = pd.read_excel(
            cache_key_historical, skiprows=2, engine="openpyxl"
        )
    return historical_df


if __name__ == "__main__":
    scrape()
