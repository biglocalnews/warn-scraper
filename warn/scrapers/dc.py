import logging
import re
import uuid
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Washington D.C.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # Get the root page
    today = datetime.today()
    current_year = today.year
    url = f"https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-{current_year}"
    r = utils.get_url(url)
    r.encoding = "utf-8"
    root_html = r.text

    # Save it to the cache
    cache.write(f"dc/{current_year}.html", root_html)

    # Parse the list of links
    soup = BeautifulSoup(root_html, "html5lib")
    table_list = soup.find_all("div", {"class": "field-items"})
    assert len(table_list) > 0

    # Grab all the links
    # link_table = table_list[0]
    # href_list = [a["href"] for a in link_table.find_all("a")]

    # As documented in #238, only the most recent pages appear to work.
    # For now, I'm going to manually set the list of links and skip scraping
    # https://github.com/biglocalnews/warn-scraper/issues/238
    # This should be replaced with something drawn from the scrape above
    # after the the bug is fixed by DC government
    href_hack = [
        "https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-2021",
        "https://does.dc.gov/node/1468786",
        "https://does.dc.gov/node/445852",
        "https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-0",
    ]

    # Download them all
    html_list = [
        root_html,
    ]
    for href in href_hack:

        # Request the HTML
        r = utils.get_url(href)
        r.encoding = "utf-8"
        html = r.text

        # Save it to the cache
        cache_key = uuid.uuid5(uuid.NAMESPACE_URL, href)
        cache.write(f"md/{cache_key}.html", html)

        # Add it to the list
        html_list.append(html)

    # Parse them all
    output_rows = []
    for i, html in enumerate(html_list):
        soup = BeautifulSoup(html, "html5lib")

        # Pull out the table
        table_list = soup.find_all("table")
        assert len(table_list) > 0
        table = table_list[0]

        # Get all rows
        row_list = table.find_all("tr")

        # If it's not the first page, slice off the header
        if i > 0:
            row_list = row_list[1:]

        # Loop through all the rows
        for row in row_list:
            # Get the cells
            cell_list = row.find_all(["td", "th"])

            # Clean them up
            cell_list = [_clean_text(c.text) for c in cell_list]

            # Pass them out
            output_rows.append(cell_list)

    # Set the export path
    data_path = data_dir / "dc.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


def _clean_text(text):
    """Clean up the provided HTML snippet."""
    if text is None:
        return ""
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


if __name__ == "__main__":
    scrape()
