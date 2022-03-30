import re
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["anikasikka"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Michigan Department of Technology, Management and Budget",
    "url": "https://milmi.org/warn/",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Michigan.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Grabs the main page with the current year's data
    current_page = utils.get_url("https://milmi.org/warn/")
    current_html = current_page.text

    # Grabs the WARN archive years html page with previous data
    archive_web_page = utils.get_url("https://milmi.org/warn/archive")
    archive_web_html = archive_web_page.text

    # Write the raw current year's file to the cache
    cache = Cache(cache_dir)
    cache.write("mi/current.html", current_html)

    # Write the archived web data to the cache
    cache = Cache(cache_dir)
    cache.write("mi/archived.html", archive_web_html)

    headers = [
        "Company Name",
        "City",
        "Date Received",
        "Incident Type",
        "Number of Layoffs",
    ]
    cleaned_data = [headers]

    # Parse current year's html file
    soup_current = BeautifulSoup(current_html, "html5lib")
    cleaned_data += _parse_html_table(soup_current.find(class_="tablewarn"))

    # Parse archived web data file
    soup_archive = BeautifulSoup(archive_web_html, "html5lib")
    cleaned_data += _parse_html_table(soup_archive)

    # Parse out PDF links for downloading
    pdf_list = []
    for link in soup_archive.select("a[href$='.pdf']"):
        # Grab the text
        link_text = link.text.strip()
        # Only keep the ones that have a four digit year in the text
        if not re.match(r"\d{4}", link_text):
            continue

        # Put the URL together
        pdf_url = f"https://milmi.org/_docs/publications/warn/warn{link_text}.pdf"

        # Download it
        cache_key = f"mi/{link_text}.pdf"
        if cache.exists(cache_key):
            pdf_file = cache_dir / cache_key
        else:
            pdf_file = cache.download(cache_key, pdf_url)
        pdf_list.append(pdf_file)

    # Set the path to the final CSV
    # We should always use the lower-case state postal code, like nj.csv
    output_csv = data_dir / "mi.csv"

    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, cleaned_data)

    # Return the path to the final CSV
    return output_csv


def _parse_html_table(soup):
    black_list = [
        "TOTAL:",
        "Number of notices received Y-T-D",
        "Total Layoffs:",
        "Notes:",
        "",
    ]
    row_list = []
    # Loop through all the rows ...
    for rows in soup.find_all("tr"):
        # Grab all the cells
        vals = []
        for data in rows.find_all("td"):
            vals.append(data.text.strip())

        # Quit if there's nothing
        if not vals:
            continue

        # If this is a blacklisted row, like the total row, skip it
        if vals[0] in black_list:
            continue

        # If we get this far, keep it
        row_list.append(vals)

    # Return the result
    return row_list


if __name__ == "__main__":
    scrape()
