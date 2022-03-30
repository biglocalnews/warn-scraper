import logging
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html", "excel"]
__source__ = {
    "name": "Illinois Department of Commerce and Economic Opportunity",
    "url": "https://www2.illinois.gov/dceo/WorkforceDevelopment/warn/Pages/default.aspx",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Illinois.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)

    state_code = "il"

    # Get the file
    url = "https://apps.illinoisworknet.com/iebs/api/public/export?search=&layoffTypes=&trade=0&dateReportedStart=Invalid%20Date&dateReportedEnd=Invalid%20Date&statuses=4&reasons=&eventCauses=&naicsCodes=1&naicIndustries=&naics=&unionsInvolved=0&geolocation=1&cities=&counties=&lwias=&includeAdditionalLwias=false&edrs=&lat=0&lng=0&distance=.5&memberType=1&users=&accessList=&bookmarked=false"
    file_path = cache.download(f"{state_code}/export.xlsx", url)

    # Parse it
    row_list = utils.parse_excel(file_path)

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
