import logging
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html", "pdf"]

logger = logging.getLogger(__name__)


FIELDS = [
    "Company Name",
    "State Notification Date",
    "Layoff Date",
    "Employees Affected",
    "Industry",
    "Attachment",
]
CSV_HEADERS = FIELDS[:-1]  # Clip the Attachment header


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Florida.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Create cache
    cache = Cache(cache_dir)

    # Request root page with PDF links
    # FL site requires realistic User-Agent.
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    url = "http://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices"
    response = utils.get_url(url, user_agent=user_agent, verify=False)
    html = response.text

    # Save it to the cache
    state_code = "fl"
    cache_key = f"{state_code}/source.html"
    cache.write(cache_key, html)

    # Pull out all the URLs for each year
    soup = BeautifulSoup(response.text, "html5lib")
    pattern = re.compile("^http://reactwarn.floridajobs.org/WarnList/")
    link_list = [i["href"] for i in soup.find_all("a", href=pattern)]

    # Separate the pdf links from the html links
    pdf_links = [link for link in link_list if "PDF" in link.upper()]
    html_links = [link for link in link_list if "PDF" not in link.upper()]

    # Pull data
    [get_or_cache(link, cache) for link in pdf_links]
    [get_or_cache(link, cache) for link in html_links]

    return data_dir / "fl.csv"


def get_or_cache(url, cache):
    """Get new URLs fresh, get old URLs from the cache."""
    current_year = datetime.now().year
    year_str = re.search(r"year=([0-9]{4})", url, re.I)
    assert year_str is not None
    year = int(year_str.group(1))
    if "PDF" in url:
        ext = "pdf"
    else:
        ext = "html"
    cache_key = f"fl/{year}.{ext}"
    if cache.exists(cache_key) and year < current_year - 1:
        return cache.path / cache_key
    else:
        return cache.download(cache_key, url, verify=False)


if __name__ == "__main__":
    scrape()
