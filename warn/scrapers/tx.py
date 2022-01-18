import re
import typing
import logging
from pathlib import Path

import pandas as pd
from xlrd import XLRDError
from bs4 import BeautifulSoup
from zipfile import BadZipFile

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Texas.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "tx.csv"
    url = "https://www.twc.texas.gov/businesses/worker-adjustment-and-retraining-notification-warn-notices#warnNotices"
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # download each year's excel file
    links = soup.find_all("a", href=re.compile("^/files/news/warn-act-listings-"))
    # create empty pandas dataframe
    output_df = pd.DataFrame()
    for link in links:
        link_url = link.get("href")
        filename_regex = re.match(r".*-(.{4})(\..*)$", link_url, re.I)
        year = int(filename_regex.group(1)[-4:])  # extract year as integer
        # only scrape after year 2019 since our historical document covers 2018 and before
        # (the historical doc includes 2019 too but the year seems to be missing some entries)
        if year >= 2019:
            file_extension = filename_regex.group(
                2
            )  # extract extension string (eg .xls, .xlsx)
            cache_path = Path(cache_dir, "tx")
            cache_path.mkdir(parents=True, exist_ok=True)
            cache_key_year = f"{cache_path}\\{year}{file_extension}"
            # get each url from the HTML links we found
            data_url = f'https://www.twc.texas.gov{link.get("href")}'
        # try to read file from cache, or download the excel file
        # (.xlsx and the older .xls files require different engines for pd.read_excel())
        try:
            logger.debug(f"Trying to read file {cache_key_year} from cache...")
            try:
                year_df = pd.read_excel(cache_key_year, engine="openpyxl")
            except BadZipFile:
                year_df = pd.read_excel(cache_key_year, engine="xlrd")
        except (FileNotFoundError, XLRDError):
            logger.debug(
                f"Failed to read file {cache_key_year} from cache. Downloading to cache from {data_url}..."
            )
            utils.download_file(data_url, cache_key_year)
            try:
                year_df = pd.read_excel(cache_key_year, engine="openpyxl")
            except BadZipFile:
                year_df = pd.read_excel(cache_key_year, engine="xlrd")
        output_df = output_df.append(year_df)
    historical_df = _scrape_historical(cache_dir)
    # flip the order of the rows to match the yearly docs
    historical_df = historical_df.iloc[::-1]
    output_df = output_df.append(historical_df)
    # drop empty columns
    output_df.dropna(inplace=True, axis=1, how="all")
    output_df.dropna(inplace=True, axis=0, how="all")
    output_df.to_csv(output_csv, index=False)
    return output_csv


# download the historical data from the cloud
def _scrape_historical(cache_dir):
    data_url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/tx_historical.xlsx"
    )
    cache_key_historical = Path(cache_dir, "tx")
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
