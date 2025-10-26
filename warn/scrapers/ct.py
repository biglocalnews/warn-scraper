import logging
from pathlib import Path

import requests

from .. import utils
from ..cache import Cache

# from bs4 import BeautifulSoup


__authors__ = [
    "zstumgoren",
    "Dilcia19",
    "stucka",
]
__tags__ = ["json"]
__source__ = {
    "name": "Connecticut Department of Labor",
    "url": "https://dolpublicdocumentlibrary.ct.gov/CsblrCategory?prefix=%2Frapid_response%2Fwarn_documents",
    "detail_url": "https://dolpublicdocumentlibrary.ct.gov/CsblrCategory/GetSpecializedData?pageSize=5000&pageIndex=1&prefix=%2Frapid_response%2Fwarn_documents&sortedCol=warn_document_date&module=WARN",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Connecticut.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    logger.debug("Seeking people-friendly page first")
    r = requests.get(__source__["url"])
    cookies = r.cookies

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "X-Security-Request": "required",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://dolpublicdocumentlibrary.ct.gov/CsblrCategory?prefix=%2Frapid_response%2Fwarn_documents",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    logger.debug("Seeking data page")

    r = requests.get(__source__["detail_url"], cookies=cookies, headers=headers)

    cache.write("fl/source.json", r.text)

    myjson = r.json()

    if myjson["totalPages"] != 1:
        logger.debug("Something went wildly wrong with pagination.")

    logger.debug(f"Looking for {len(myjson['blobItems']):,} entries in the data.")
    masterlist = []

    for entry in myjson["blobItems"]:
        line = {}

        # Flatten the structure here
        for item in entry["blobProperties"]:
            entry[item] = entry["blobProperties"][item]
        for item in entry:
            if item != "blobProperties":
                line[item.strip("_")] = entry[item]
        masterlist.append(line)
    logger.debug(f"Added {len(masterlist):,} records from the data.")

    # Set the export path
    data_path = data_dir / "ct.csv"

    # Write out to csv
    utils.write_disparate_dict_rows_to_csv(data_path, masterlist, mode="w")

    # Return the path
    return data_path


if __name__ == "__main__":
    scrape()
