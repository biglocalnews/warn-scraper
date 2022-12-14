import logging
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212", "palewire"]
__tags__ = ["html"]
__source__ = {
    "name": "Wisconsin Department of Workforce Development",
    "url": "https://dwd.wisconsin.gov/dislocatedworker/warn/",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Wisconsin.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # Get the current year
    today = datetime.today()
    current_year = today.year

    # Get the current year of data
    url = "https://dwd.wisconsin.gov/dislocatedworker/warn/"
    r = utils.get_url(
        url,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    )
    html = r.text
    cache.write(f"wi/{current_year}.html", html)
    html_list = [html,]

    # Set the date range we're going to scrape
    year_range = list(range(2016, current_year + 1))
    year_range.reverse()

    # Loop through the years and download the pages
    for year in year_range:
        # Since the current year page doesn't exist, we're going to hack in a skip
        if year == current_year:
            continue

        # Request fresh pages, use cache for old ones
        cache_key = f"wi/{year}.html"
        if cache.exists(cache_key) and year < current_year - 1:
            html = cache.read(cache_key)
        else:
            url = f"https://dwd.wisconsin.gov/dislocatedworker/warn/{year}/default.htm"
            r = utils.get_url(url)
            html = r.text
            cache.write(cache_key, html)

        # Add to the list
        html_list.append(html)

    header = [
        "Company",
        "City",
        "Affected Workers",
        "Notice Received",
        "Original Notice Type / Update Type",
        "Layoff Begin Date",
        "NAICS Description",
        "County"
        "Workforce Development Area"
    ]
    output_rows = [header,]
    for html in html_list:
        # Parse the HTML
        soup = BeautifulSoup(html, "html5lib")

        # Fish out the tables
        table_list = soup.find_all("table")

        # Remove the "Updates to Previously Filed Notices" tables
        # We can single them out because they only have two columns
        notice_tables = [t for t in table_list if len(t.find("tr").find_all("th")) > 2]

        # Loop through the tables
        for table in notice_tables:
            # Get all the rows
            for row in table.find_all("tr"):
                # Pull out the cells and clean them
                cell_list = [_clean_text(c.text) for c in row.find_all(["td"])]

                # Skip empty rows
                try:
                    # A list with only empty cell will throw an error
                    next(i for i in cell_list if i)
                except StopIteration:
                    continue

                # Tack what we've got onto the pile
                output_rows.append(cell_list)

    # Set the export path
    data_path = data_dir / "wi.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


def _clean_text(text):
    """Clean up the provided cell."""
    # remove trailing characters after LayoffBeginDate
    if re.match(r"^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", text):
        text = re.sub(r"(?<=[0-9]{4}).*", "", text)
    return text.strip()


if __name__ == "__main__":
    scrape()
