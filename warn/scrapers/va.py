import datetime
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
    cache = Cache(cache_dir)
    csv_url = "https://vec.virginia.gov/warn-notices-csv.csv"

    """
    This scraper originally tried to parse HTML to find a CSV download link.
    The HTML scraping portion broke in early December 2024. The code had
    also been downloading an incomplete slice of the data.

    In late December 2024, everything broke because Virginia decided to begin
    testing for Javascript-aware browsers. This code is the way it is because
    every alternative considered was somehow worse. Not helping? Losing about
    four hours of work including the extensive documentation on the
    alternatives sought.

    Virginia's protections require a JS-aware browser to evaluate some
    obscurred, frequently changing code to set some short-lived cookies.
    Without those cookies, no code. And even headless browsers get blocked
    by a video test. Really unfun. So a ... headed? ... JS-aware browser
    is required.

    Some things evaluated included, off memory:

    -- Using Playwright instead. This looked like a reasonable approach but
        was awful resource-wise. Playwright itself had significant overhead,
        partially from requiring its own version of browsers to be installed.
        There's apparently some way with YAML to try to get Github Actions,
        where this project is in production, to install only for particular
        branches. Without that code, this'd be pending a couple minutes
        several times a day on each of about 40 different branches of code.
    -- Using Selenium. This is where it ultimately landed. It's not great,
        but after trying about a dozen alernatives it's the best we got.
    -- Installation code for Chrome's driver started acting flaky between
        platforms.
    -- PhantomJS couldn't even get past the first brush with the protection.
    -- The optimal file is the CSV created by the state with well-defined
        fields. Unfortunately, hitting the link once approved by the
        Javascript results in an immediate download. There's no regular way
        to get the file path through Javascript. Backdoor efforts like trying
        to go through the Download menu also failed, because Chrome puts
        them into a Shadow DOM. Several hunks of code to try to access the
        Shadow DOM and get at the local filename are no longer functional
        in Chrome. Building an extension to track some of this ... is not
        an option, and loading it the first time would require human
        intervention rather than automation. There might be a way to mess
        with the Shadow DOM through CSS manipulation, but that looked to
        weird to bother trying especially given other more reasonable measures
        that no longer worked.
    -- Also, efforts to get at the CSV through view-source failed.
    -- And it's possible to scrape the HTML and try to parse it back out for
        what warn-scraper needs, but that seemed even more fraught than trying
        to get the CSV.
    -- So if the filename isn't obtainable through Chrome, where do we get it?
        There's a multiplatform way to get at a user's home directory. For
        many people Downloads is off there, at ... ~/Downloads, capital D,
        plural. Except people can configure that differently. And most
        languages won't call it Downloads. And Chrome of course lets people
        set a default download location that can be anywhere else, or select
        a per-file location ("Ask me where to save this" or some such).
        After going down even more rabbit holes, ... ~/Downloads is all that
        gets implemented here.
    -- I tried to see if Firefox might be a little less grumpy. One Python
        driver-finder got one day of commits. A fork has Issues turned off
        somehow. The third one I looked at was the one that was grumpy for
        Chrome, and its maintainer is apparently trying to protect his
        homeland with FPV drones. So ... back to Chrome.

    So, yes, this is a weird implementation. It's a terrible model. It's
    even got a hard-coded wait. At least as of late December 2024, however,
    it does work. ... in late December 2024.
    """

    # driver = webdriver.Chrome(options=chromeoptionsholder, service=Service(ChromeDriverManager().install()))
    logger.debug("Attempting to launch Chrome")
    chromeoptionsholder = ChromeOptions()
    chromeoptionsholder.add_argument("--no-sandbox")
    chromeoptionsholder.add_argument("--disable-dev-shm-usage")
    chromeoptionsholder.add_argument("--remote-debugging-pipe")
    chromeoptionsholder.add_argument("--verbose")

    chrome_install = ChromeDriverManager().install()

    # Weird error with finding the driver name in Windows. Sometimes.
    if chrome_install.endswith("THIRD_PARTY_NOTICES.chromedriver"):
        chrome_install = chrome_install.replace(
            "THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe"
        )
    logger.debug(f"Chrome install variable is {chrome_install}")
    # folder = os.path.dirname(chrome_install)
    # chromedriver_path = folder #  os.path.join(folder, "chromedriver.exe")
    # service = ChromeService(chromedriver_path)
    service = ChromeService(chrome_install)
    driver = webdriver.Chrome(options=chromeoptionsholder, service=service)
    logger.debug(f"Attempting to fetch {csv_url}")
    driver.get(csv_url)

    sleep(30)  # Give it plenty of time to evaluate Javascript

    download_dir = os.path.expanduser("~") + "/Downloads"

    if not os.path.isdir(download_dir):
        logger.error(f"The download directory is not {download_dir}.")

    # get the list of files
    list_of_files = glob(download_dir + "/warn-notices-csv*.csv")
    if len(list_of_files) == 0:
        logger.error(f"No matching files found in {download_dir}.")

    # get the latest file name
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_file_time = datetime.datetime.fromtimestamp(os.path.getctime(latest_file))

    # print the latest file name
    logger.debug(f"CSV saved to {latest_file}, saved at {latest_file_time}")

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
