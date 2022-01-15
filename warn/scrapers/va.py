import logging

import requests
from bs4 import BeautifulSoup

from warn.utils import download_file

logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    """
    Scrape data from Virginia.

    Arguments:
    output_dir -- the Path were the result will be saved

    Keyword arguments:
    cache_dir -- the Path where results can be cached (default None)

    Returns: the Path where the file is written
    """
    output_csv = f"{output_dir}/va.csv"
    url = "https://www.vec.virginia.gov/warn-notices"
    response = requests.get(url)
    logger.debug(f"Page status is {response.status_code} for {url}")
    soup = BeautifulSoup(response.text, "html.parser")
    data_url = soup.find("a", text="Download")["href"]
    data_url = f"https://www.vec.virginia.gov{data_url}"
    download_file(data_url, output_csv)
    return output_csv
