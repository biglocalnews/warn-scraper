import logging
import re
from datetime import datetime
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["palewire"]
__tags__ = [
    "html",
    "pdf",
]
__source__ = {
    "name": "South Carolina Department of Employment and Workforce",
    "url": "https://scworks.org/employer/employer-programs/at-risk-of-closing/layoff-notification-reports",
}


logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from South Carolina.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get URL
    r = utils.get_url(
        "https://scworks.org/employer/employer-programs/risk-closing/layoff-notification-reports",
        verify=False,
    )
    html = r.text

    # Save it to the cache
    cache = Cache(cache_dir)
    cache.write("sc/source.html", html)

    # Parse out the PDF links
    soup = BeautifulSoup(html, "html.parser")
    link_list = soup.find_all("a")
    pdf_dict = {}
    for a in link_list:
        # Pull the data we want to keep
        try:
            a_href = a["href"]
        except KeyError:
            # Skip non-links
            continue
        a_text = a.text.strip()
        if "pdf" in a_href:
            # Make sure that the text is a year
            try:
                a_year = int(a_text[:4].strip())
            except ValueError:
                logger.info(f"'{a_text}' link does not parse as a year")
                continue
            # Make sure the links are unique
            if a_year not in pdf_dict:
                pdf_dict[a_year] = a_href
    logger.debug(f"{len(pdf_dict)} PDF links identified")

    # Pattern to find and extract data cells
    naics_re = re.compile("^[0-9]{5,6}$")
    date_re = re.compile("^[0-9]{1,2}/[0-9]{1,2}[/]{1,2}[0-9]{2}")
    jobs_re = re.compile("^[0-9]{1,4}$")

    current_year = datetime.now().year
    output_rows = []
    for pdf_year, pdf_href in pdf_dict.items():
        cache_key = f"sc/{pdf_year}.pdf"
        if cache.exists(cache_key) and pdf_year < (current_year - 1):
            pdf_path = cache.path / cache_key
        else:
            pdf_path = cache.download(
                cache_key, f"https://scworks.org/{pdf_href}", verify=False
            )

        # Open the PDF
        with pdfplumber.open(pdf_path) as pdf:

            # Loop through the pages
            for page in pdf.pages:

                # Pull out the table
                row_list = page.extract_table()

                # Skip empty pages
                if not row_list:
                    continue

                # Skip skinny and empty rows
                real_rows = []
                for row in row_list:
                    values = [v for v in row if v]
                    if len(values) < 4:
                        continue
                    real_rows.append(row)

                # Loop through each row in the table
                for row in real_rows:

                    # Clean values
                    cell_list = [_clean_cell(c) for c in row if _clean_cell(c)]

                    # Pluck out the values based on our regex
                    d = {}
                    for cell in cell_list:
                        if naics_re.search(cell):
                            d["naics"] = cell
                        elif date_re.search(cell):
                            d["date"] = cell
                        elif jobs_re.search(cell):
                            d["jobs"] = int(cell)

                    # If there haven't been at least two matches, it must be junk
                    if len(d) < 2:
                        continue

                    # The first one should be the company
                    d["company"] = cell_list[0]

                    # The second one should be the location
                    d["location"] = cell_list[1]

                    # Tack in the source PDF
                    d["source"] = cache_key

                    # Keep what we got
                    output_rows.append(d)

    # Write out the data to a CSV
    data_path = data_dir / "sc.csv"
    headers = ["company", "location", "date", "jobs", "naics", "source"]
    utils.write_dict_rows_to_csv(data_path, headers, output_rows, extrasaction="ignore")

    # Return the Path to the CSV
    return data_path


def _clean_cell(cell):
    """Clean the value in the provided cell."""
    if cell is None:
        return None
    return cell.strip().replace("\n", "")


if __name__ == "__main__":
    scrape()
