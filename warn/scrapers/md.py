import logging
import re
from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html"]
__source__ = {
    "name": "Maryland Department of Labor",
    "url": "https://www.dllr.state.md.us/employment/warn.shtml",
}

logger = logging.getLogger(__name__)

naptime = 3


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Maryland.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # In November 2024 Maryland began throwing out many failed connection messages. These two things helped.
    request_headers = {"User-Agent": "BigLocalNews.org"}
    request_verify = False

    # Get the page
    url = "https://www.dllr.state.md.us/employment/warn.shtml"
    r = utils.get_url(url, headers=request_headers, verify=request_verify)
    r.encoding = "utf-8"
    html = r.text

    # Save it to the cache
    cache.write("md/source.html", html)

    sleep(naptime)  # Try to stop blocked connections by being less aggressive

    # Parse the list of links
    soup = BeautifulSoup(html, "html.parser")
    a_list = soup.find_all("a", {"class": "sub"})
    href_list = [a["href"] for a in a_list]

    # Download them all
    html_list = []
    html_list.append(html)  # Save the source HTML for parsing also

    old_pages = [
        "warn2023.shtml",
        "warn2022.shtml",
        "warn2021.shtml",
        "warn2020.shtml",
        "warn2019.shtml",
        "warn2018.shtml",
        "warn2017.shtml",
        "warn2016.shtml",
        "warn2015.shtml",
        "warn2014.shtml",
        "warn2013.shtml",
        "warn2012.shtml",
        "warn2011.shtml",
        "warn2010.shtml",
    ]

    for href in href_list:
        # Request the HTML
        url = f"https://www.dllr.state.md.us/employment/{href}"
        filename = f"md/{href}.html"

        if href not in old_pages:
            sleep(naptime)  # Try to stop blocked connections by being less aggressive
            r = utils.get_url(url, headers=request_headers, verify=request_verify)
            r.encoding = "utf-8"
            html = r.text

            # Save it to the cache
            cache.write(filename, html)
        else:
            r = utils.fetch_if_not_cached(
                cache_dir / filename,
                url,
                headers=request_headers,
                verify=request_verify,
            )
            html = cache.read(filename)

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
            cell_list = row.find_all("td")

            # Clean them up
            cell_list = [_clean_text(c.text) for c in cell_list]

            # Pass them out
            output_rows.append(cell_list)

    # Set the export path
    data_path = data_dir / "md.csv"

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
