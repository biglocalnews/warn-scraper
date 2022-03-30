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
__source__ = {
    "name": "District of Columbia Department of Employment Services",
    "url": f"https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-{datetime.today().year}",
}

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
    link_table = table_list[0]
    link_lookup = {_extract_year(a.string): a["href"] for a in link_table.find_all("a")}

    # As documented in #238, the page for 2014 is missing. We're
    # testing whether the URL for the 2019 page is the same as the
    # the 2014 link currently points to and scraping an archived copy
    # from 2017 instead.
    if link_lookup.get("2014") == link_lookup.get("2018"):
        logger.warning("2014 link is the same as 2018 link, using archived 2014")
        link_lookup[
            "2014"
        ] = "https://web.archive.org/web/20170210010137/http://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-closure%202014"

    # Download them all
    html_list = [
        root_html,
    ]
    for href in link_lookup.values():

        # Request the HTML
        r = utils.get_url(href)
        r.encoding = "utf-8"
        html = r.text

        # Save it to the cache
        cache_key = uuid.uuid5(uuid.NAMESPACE_URL, href)
        cache.write(f"dc/{cache_key}.html", html)

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

            # Add to the list if any cell in the row has data
            # (filters out empty rows)
            if any(cell_list):
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


def _extract_year(text):
    """Extract the year from the string."""
    if text is None:
        return None
    return re.sub(r"\D", "", text)


if __name__ == "__main__":
    scrape()
