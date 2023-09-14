import csv
import json
import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .. import utils

__authors__ = ["zstumgoren", "Dilcia19", "chriszs", "stucka"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Ohio Department of Job and Family Services",
    "url": "https://jfs.ohio.gov/warn/index.stm",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Ohio.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    state_code = "oh"

    # Get the latest HTML
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
    }

    latesturl = "https://jfs.ohio.gov/wps/portal/gov/jfs/job-services-and-unemployment/job-services/job-programs-and-services/submit-a-warn-notice/current-public-notices-of-layoffs-and-closures-sa/current-public-notices-of-layoffs-and-closures"

    logger.debug("Attempting to fetch current data")
    r = requests.get(latesturl, headers=headers)
    soup = BeautifulSoup(r.content)
    logger.debug("Attempting to get JSON data from Ohio file")
    mydiv = soup.find("div", {"id": "js-placeholder-json-data"})
    mydata = json.loads(mydiv.decode_contents().strip())["data"]
    rawheaders = mydata[1]
    masterlist = []
    for row in mydata[2:]:
        if len(row) == len(rawheaders):
            line = {}
            for i, item in enumerate(rawheaders):
                if item != "":
                    line[item] = row[i]
            masterlist.append(line)

    logger.debug("Get historical data and meld it into current format")
    # Get the historical data, and meld it into the same format
    lookup = {
        "Company": "Company",
        "DateReceived": "Date Received",
        "URL": None,
        "City/County": "City/County",
        "Potential NumberAffected": "Potential Number Affected",
        "LayoffDate(s)": "Layoff Date(s)",
        "PhoneNumber": "Phone Number",
        "Union": "Union",
        "Notice ID": "Notice ID",
    }

    r = requests.get(
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/oh_historical.csv"
    )
    reader = list(csv.DictReader(r.text.splitlines()))
    for row in reader:
        line = {}
        for item in lookup:
            if not lookup[item]:
                line[item] = None
            else:
                line[lookup[item]] = row[item]
        masterlist.append(line)

    # Write out
    data_path = data_dir / f"{state_code}.csv"

    utils.write_dict_rows_to_csv(
        data_path,
        list(masterlist[0].keys()),
        masterlist,
        mode="w",
        extrasaction="raise",
    )

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
