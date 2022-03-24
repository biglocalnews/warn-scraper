import re
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

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
    cache.write("mi/current/source.html", current_html)

    # Write the archived web data to the cache
    cache = Cache(cache_dir)
    cache.write("mi/archived/source.html", archive_web_html)

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
        "",
    ]

    # Parses current year's html file

    soup_current = BeautifulSoup(current_html, "html5lib")

    # Goes through the current data
    for rows in soup_current.find(class_="tablewarn").find_all("tr"):
        vals = []
        for data in rows.find_all("td"):
            vals.append(data.text.strip())
        if vals:
            if vals[0].strip() in header_blacklist:
                continue
        cleaned_data.append(vals)

    # Parses archived web data file

    soup_web_archive = BeautifulSoup(archive_web_html, "html5lib")
    for rows in soup_web_archive.find_all("tr"):
        vals = []
        for data in rows.find_all("td"):
            vals.append(data.text.strip())
        if vals:
            if vals[0].strip() in header_blacklist:
                continue
        cleaned_data.append(vals)

    for link in enumerate(soup_web_archive.select("a[href$='.pdf']")):
        link_text = str(link).strip()
        if not re.match(r"\d{4}", link_text):
            continue
        pdf_url = "https://milmi.org/_docs/publications/warn/warn" + link_text + ".pdf"
        pdf_file = cache.download("mi/pdffile.pdf", pdf_url)

        with pdfplumber.open(pdf_file) as pdf:
            for my_page in pdf.pages:
                text = my_page.extract_text()
                data = []
                row_list = text.split("\n")
                for i, row in enumerate(row_list):
                    if i <= 5:
                        continue
                    first_split = re.split(r"\s{3,}", str(row))
                    assert len(first_split) == 3
                    company = first_split[0]
                    location = first_split[1]
                    second_split = first_split[2].split()
                    assert len(second_split) == 3
                    date_received, layoff_type, jobs_affected = second_split
                    cleaned_data.append(
                        [company, location, date_received, layoff_type, jobs_affected]
                    )
    final_data = []
    for data in cleaned_data:
        if len(data) == 0:
            continue
        final_data.append(data)

    # Set the path to the final CSV
    # We should always use the lower-case state postal code, like nj.csv
    output_csv = data_dir / "mi.csv"

    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, final_data)

    # Return the path to the final CSV
    return output_csv


if __name__ == "__main__":
    scrape()
