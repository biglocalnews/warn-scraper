import csv
import logging
import re
from glob import glob
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .. import utils

__authors__ = ["chriszs", "esagara", "Ash1R", "stucka"]
__tags__ = ["html"]
__source__ = {
    "name": "Georgia Department of Labor",
    "url": "https://www.dol.state.ga.us/public/es/warn/searchwarns/list",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Georgia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    base_url = "https://www.tcsg.edu/warn-public-view/"

    api_url = "https://www.tcsg.edu/wp-admin/admin-ajax.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }

    response = utils.get_url(base_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, features="html5lib")

    script = str(
        soup.find(
            "script", text=lambda text: text and "window.gvDTglobals.push" in text
        )
    )

    match = re.search(r'"nonce":"([^"]+)"', script)
    if match:
        nonce = match.group(1)
        logger.debug(f"Nonce value found: {nonce}")
    else:
        logger.debug(
            "Nonce value not parsed from page; scrape will likely break momentarily."
        )

    payload = {
        "draw": 1,
        "columns": [
            {
                "data": 0,
                "name": "gv_96",
                "searchable": True,
                "orderable": True,
                "search": {
                    "value": None,
                    "regex": False,
                },
            },
            {
                "data": 1,
                "name": "gv_4",
                "searchable": True,
                "orderable": True,
                "search": {
                    "value": None,
                    "regex": False,
                },
            },
            {
                "data": 2,
                "name": "gv_date_created",
                "searchable": True,
                "orderable": True,
                "search": {
                    "value": None,
                    "regex": False,
                },
            },
            {
                "data": 3,
                "name": "gv_97",
                "searchable": True,
                "orderable": True,
                "search": {
                    "value": None,
                    "regex": False,
                },
            },
        ],
        "order": [{"column": 0, "dir": "asc"}],
        "start": 0,
        "length": -1,
        "search": {
            "value": None,
            "regex": False,
        },
        "action": "gv_datatables_data",
        "view_id": 77460,
        "post_id": 77462,
        "nonce": nonce,
        "getData": [],
        "hideUntilSearched": 0,
        "setUrlOnSearch": True,
        "shortcode_atts": {"id": 77460, "class": None, "detail": None},
    }
    response = requests.post(api_url, data=payload, headers=headers)

    # Use JSON as an index to get other data files
    data = response.json()["data"]
    logger.debug(f"{len(data):,} records from newer dataset in index.")

    # Download detailed data if not already cached
    for listing in data:
        filehref = BeautifulSoup(listing[0], features="html5lib")("a")[0]["href"]
        fileid = BeautifulSoup(listing[0], features="html5lib")("a")[0].contents[0]
        targetfilename = cache_dir / ("ga/" + fileid + ".format3")
        utils.fetch_if_not_cached(targetfilename, filehref)

    # Parse detailed data
    masterlist = []
    for filename in glob(f"{cache_dir}/ga/*.format3"):
        with open(filename, "r", encoding="utf-8") as infile:
            html = infile.read()
        tableholder = BeautifulSoup(html, features="html5lib").find(
            "table", {"class": "gv-table-view-content"}
        )
        lastrowname = "Placeholder"
        line = {}
        for row in tableholder.find_all("tr")[1:]:  # Skip header row
            if (
                row.find_all("table")
                or not row.find_all("th")
                or not row.find_all("td")
            ):  # Then it's a little sideshow and we don't care.
                pass
            else:
                rowname = row.find("th").text
                if not rowname:
                    rowname = lastrowname + "."
                lastrowname = rowname
                if (
                    "Email" not in rowname
                    and "Submitter Information" not in rowname
                    and "Acknowledgement" not in rowname
                ):
                    rowcontent = row.find("td").text
                    if "Location Address" in rowname or rowname == "Company Address":
                        rowguts = (
                            str(row.find("td"))
                            .split("<br/><a")[0]
                            .replace("<td>", "")
                            .replace("<br/>", ", ")
                        )
                        rowcontent = rowguts
                    line[rowname] = rowcontent
        masterlist.append(line)

    headermatcher = {
        "ID": "GA WARN ID",
        "Company Name": "Company Name",
        "City": "First Location Address",
        "ZIP": "Zip Code",
        "County": "County",
        "Est. Impact": "Total Number of Affected Employees",
        "LWDA": "LWDA",  # Not used in newer format
        "Separation Date": "First Date of Separation",
    }

    # Get and process historical data
    historicalfilename = cache_dir / ("ga/ga_historical.csv")
    filehref = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/ga_historical.csv"
    )
    utils.fetch_if_not_cached(historicalfilename, filehref)
    with open(historicalfilename, "r", encoding="utf-8") as infile:
        reader = list(csv.DictReader(infile))
        logger.debug(f"Found {len(reader):,} historical records.")
        for row in reader:
            line = {}
            for item in headermatcher:
                line[headermatcher[item]] = row[item]
            masterlist.append(line)
    logger.debug(f"{len(masterlist):,} records now included.")

    masterheaders = []
    for row in masterlist:
        for key in list(row.keys()):
            if key not in masterheaders:
                masterheaders.append(key)

    output_csv = data_dir / "ga.csv"

    # This utils writer function presumes every row has the same format, and ... they don't. So let's standardize.
    for i, row in enumerate(masterlist):
        line = {}
        for item in masterheaders:
            if item in row:
                line[item] = row[item]
            else:
                line[item] = None
        masterlist[i] = line

    utils.write_dict_rows_to_csv(
        Path(output_csv), masterheaders, masterlist, mode="w", extrasaction="raise"
    )

    return output_csv


if __name__ == "__main__":
    scrape()
