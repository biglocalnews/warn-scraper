import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup
import requests

from .. import utils

__authors__ = ["chriszs, esagara, Ash1R", "stucka"]
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
    soup = BeautifulSoup(response.text)

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
        "length": 25,
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
    pdf_headers = ["company", "date", "# affected", "url"]
    final = [pdf_headers]
    data = response.json()["data"]
    logger.debug(f"{len(data):,} data entries found")
    for listing in data:
        row = []
        row.append(listing[1])
        row.append(listing[2])
        row.append(listing[3])
        row.append(BeautifulSoup(listing[0]).text)
        final.append(row)
    output_csv = data_dir / "ga.csv"
    utils.write_rows_to_csv(output_csv, final)
    return output_csv


if __name__ == "__main__":
    scrape()
