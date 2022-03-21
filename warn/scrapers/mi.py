from pathlib import Path

import pdfplumber
from .. import utils
from ..cache import Cache

from bs4 import BeautifulSoup

__authors__ = ["anikasikka"]
__tags__ = ["html", "pdf"]

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
    cache.write("mi_current/source.html", current_html)

    # Write the archived web data to the cache
    cache = Cache(cache_dir)
    cache.write("mi_archived/source.html", archive_web_html)

    # Set the headers for all sources
    mi_headers = [
        "Company Name", 
        "City", 
        "Date Received", 
        "Incident Type", 
        "Number of Layoffs",
    ]

    cleaned_data = [mi_headers]

    header_blacklist = [
        "TOTAL:", 
        "Number of notices received Y-T-D", 
        "Total Layoffs:", 
        "Notes:",
        ""
    ]

    # Parses current year's html file

    soup_current = BeautifulSoup(current_html, "html5lib")

    # Goes through the current data 
    for rows in soup_current.find_all('tr'):
        vals = []
        for data in rows.find_all('td'):
            vals.append(data.text.strip())
        cleaned_data.append(vals)

    # Parses archived web data file

    soup_web_archive = BeautifulSoup(archive_web_html, "html5lib")
    for rows in soup_web_archive.find_all('tr'):
        vals = []
        for data in rows.find_all('td'):
            vals.append(data.text.strip())
        cleaned_data.append(vals)

    for i, link in enumerate(soup_web_archive.select("a[href$='.pdf']")):
        if (i == 0 or i == 1): 
            continue
        pdf_url = ("https://milmi.org/_docs/publications/warn/warn" + link.text.strip() + ".pdf")
        pdf_file = cache.download("mi/pdffile.pdf", pdf_url)

        with pdfplumber.open(pdf_file) as pdf:
            for my_page in pdf.pages:
                text = my_page.extract_text()
                data = []
                for i, row in enumerate (text.split("\n")):
                    if i in range(0, 5): 
                        continue
                    data.append(str(row))
                for vals in data: 
                    cleaned_data.append(vals.rsplit(" ")) 

    # Set the path to the final CSV
    # We should always use the lower-case state postal code, like nj.csv
    output_csv = data_dir / "mi.csv"

    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, cleaned_data)

    # Return the path to the final CSV
    return output_csv


if __name__ == "__main__":
    scrape()