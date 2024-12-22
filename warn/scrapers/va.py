import logging
import os
from glob import glob
from pathlib import Path
from shutil import copyfile
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly", "stucka"]
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
    # This scraper initially tried to get a CSV download link that was only for the most recent entries. The scraping part of that broke.
    # It's now hard-coded to a particular download link with parameters that should get the full thing.

    # This may break again, but this revised attempt has far fewer moving parts and actually fetches the complete data set.
    # Blame Stucka in December 2024.
    # And it broke again in December 2024, but not even Stucka will blame Stucka for this mess.

    cache = Cache(cache_dir)
    #     csv_url = "https://vec.virginia.gov/warn-notices-csv.csv?field_notice_date_value%5Bmin%5D%5Bdate%5D=1%2F1%2F1990&field_notice_date_value%5Bmax%5D%5Bdate%5D=&field_region_warn_tid=All"

    csv_url = "https://vec.virginia.gov/warn-notices-csv.csv"

    # driver = webdriver.Chrome(options=chromeoptionsholder, service=Service(ChromeDriverManager().install()))
    logger.debug("Attempting to launch Chrome")
    chromeoptionsholder = ChromeOptions()
    chrome_install = ChromeDriverManager().install()
    folder = os.path.dirname(chrome_install)
    chromedriver_path = os.path.join(folder, "chromedriver.exe")
    service = ChromeService(chromedriver_path)
    driver = webdriver.Chrome(options=chromeoptionsholder, service=service)
    logger.debug(f"Attempting to fetch {csv_url}")
    driver.get(csv_url)

    sleep(25)

    logger.debug(driver.page_source)

    # get the user download folder (dynamic so will work on any machine)
    downLoadFolder = os.path.join(os.getenv("USERPROFILE"), "Downloads")  # type: ignore
    # get the list of files
    list_of_files = glob(downLoadFolder + "/*.csv")
    # get the latest file name
    latest_file = max(list_of_files, key=os.path.getctime)
    # print the latest file name
    logger.debug(f"CSV saved to {latest_file}")

    target_filename = cache_dir / "va" / "source.csv"

    utils.create_directory(path=cache_dir / "va", is_file=False)

    logger.debug(f"Saving file to {target_filename}")

    copyfile(latest_file, target_filename)

    driver.quit()

    # Download it to the cache
    # cache.download("va/source.csv", csv_url, verify=True)

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
