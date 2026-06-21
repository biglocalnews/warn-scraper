import csv
import logging
from io import StringIO
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "stucka"]
__tags__ = [
    "csv",
]
__source__ = {
    "name": "Alabama Department of Commerce",
    "url": "https://www.madeinalabama.com/warn-list/",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Alabama.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache()
    output_csv = data_dir / "al.csv"

    # page = utils.get_url("https://www.madeinalabama.com/warn-list/")
    # URL change in June 2026, maybe led to a HTTP 415 error
    # page = utils.get_url("https://workforce.alabama.gov/warn-list/")
    # Later in June 2026, they're detecting the automation and blocking us.
    # But say they won't for the CSV download which, OK.
    # No headers on the CSV, which they'll probably realize ... sometime.

    targeturl = "https://workforce.alabama.gov/documents/warn-list/"
    page = utils.get_url(targeturl).text
    cache.write("al/rawcsv.csv", page)

    headers = [
        "_id1",
        "action_type",
        "date_notice",
        "date_action",
        "company",
        "location",
        "affected",
        "_id2",
    ]

    fileholder = StringIO(page)

    reader = list(csv.DictReader(fileholder, fieldnames=headers))

    utils.write_disparate_dict_rows_to_csv(
        output_csv, reader, mode="w", prefixes=["_id"]
    )

    return output_csv


if __name__ == "__main__":
    scrape()
