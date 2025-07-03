import datetime
import logging
import os
import platform

# import subprocess
from glob import glob
from pathlib import Path
from random import random
from shutil import copyfile
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from stealthenium import stealth
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

if platform.system() == "Windows":
    message = "This scraper requires Xvfb, which does not appear to be "
    message += "supported within Windows, even with WSL. This scraper "
    message += "will not work for you."
    logger.error(message)
    quit()
else:
    print(f"{platform.system} found")
    from xvfbwrapper import Xvfb


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
    # csv_url = "https://vec.virginia.gov/warn-notices-csv.csv"
    start_page = "https://www.virginiaworks.gov/warn-notices/"
    csv_url = "https://vec.virginia.gov/warn_notices.csv"

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

    And then it broke in early January 2025! But it's not an IP block.
    They may have started blocking direct calls to the CSV. Code patched
    in late January 2025 to use the Download button.
    """

    # driver = webdriver.Chrome(options=chromeoptionsholder, service=Service(ChromeDriverManager().install()))
    logger.debug("Attempting to launch Chrome")
    chromeoptionsholder = ChromeOptions()
    chromeoptionsholder.add_argument("--no-sandbox")
    chromeoptionsholder.add_argument("--disable-dev-shm-usage")
    chromeoptionsholder.add_argument("--remote-debugging-pipe")
    chromeoptionsholder.add_argument("--verbose")
    chromeoptionsholder.add_argument("start-maximized")
    chromeoptionsholder.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )
    chromeoptionsholder.add_experimental_option("useAutomationExtension", False)
    chromeoptionsholder.add_argument("--disable-blink-features=AutomationControlled")

    if "CHROMEWEBDRIVER" in os.environ:
        chrome_install = os.environ["CHROMEWEBDRIVER"] + "/chromedriver"
    else:
        chrome_install = ChromeDriverManager().install()

        # Weird error with finding the driver name in Windows. Sometimes.
        if chrome_install.endswith("THIRD_PARTY_NOTICES.chromedriver"):
            chrome_install = chrome_install.replace(
                "THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe"
            )
    logger.debug(f"Chrome install variable is {chrome_install}")

    # Hack on chromedriver itself, to try to be sneakier
    # So many bad ideas coming together here
    # perlstr = f"perl -pi -e 's/cdc_/ugh_/g' {chrome_install}"
    # logger.debug(perlstr)
    # process = subprocess.run(perlstr.split(), capture_output=True, text=True)
    # logger.debug(f"process stdout: {process.stdout}")
    # logger.debug(f"process stderr: {process.stderr}")

    # Launch X Windows emulator, then launch Chrome to run with it
    with Xvfb() as xvfb:  # noqa: F841
        service = ChromeService(chrome_install, service_args=["--verbose"])
        # driver = webdriver.Chrome(options=chromeoptionsholder, service=service)
        # driver = webdriver.Remote(options=chromeoptionsholder, service=service)
        # capabilities = DesiredCapabilities.CHROME.copy()
        # driver = webdriver.Remote(options=chromeoptionsholder, desired_capapabilities=capabilities, command_executor="http://localhost:4444/wd/hub")
        # driver = webdriver.Chrome(options=chromeoptionsholder, service=service)
        service = ChromeService(chrome_install, service_args=["--verbose"], port=5600)
        driver = webdriver.Chrome(options=chromeoptionsholder, service=service)
        driver.command_executor._url = "http://localhost:5600"
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        logger.debug(f"Attempting to fetch {start_page}")
        driver.get(start_page)
        sleep((4 * random()) + 8)
        # with open("va-weird.html", "w") as outfile:
        #     outfile.write(driver.page_source)
        # driver.find_element(By.ID, "warn-notice-well").find_element(
        #     By.PARTIAL_LINK_TEXT, "Download"
        # ).click()

        # driver.find_element(By.PARTIAL_LINK_TEXT, "Download Full List of WARN notices").click()

        # element = driver.find_element(By.CSS_SELECTOR, "#warn-notice-well a img")
        element = driver.find_element(By.CSS_SELECTOR, "#warn-notice-well a")
        logger.debug(f"Element found: {element.get_attribute('outerHTML')}")
        driver.execute_script("arguments[0].click();", element)
        # element.click()

        logger.debug(f"Attempting to fetch {csv_url}")
        # driver.get(csv_url)
        sleep(45)  # Give it plenty of time to evaluate Javascript
        # driver.get(csv_url)
        # sleep(10)
        driver.quit()

    download_dir = os.path.expanduser("~") + "/Downloads"

    if not os.path.isdir(download_dir):
        logger.error(f"The download directory is not {download_dir}.")

    # get the list of files
    list_of_files = glob(download_dir + "/warn_notices*.csv")
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
