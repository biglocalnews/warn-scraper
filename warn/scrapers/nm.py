import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["pdf"]
__source__ = {
    "name": "New Mexico Department of Workforce Solutions",
    "url": "https://www.dws.state.nm.us/Rapid-Response",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from New Mexico.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Fire up the cache
    cache = Cache(cache_dir)

    # Download the root page
    base_url = "https://www.dws.state.nm.us/"
    url = f"{base_url}Rapid-Response"
    page = utils.get_url(url)
    html = page.text

    # Save it to the cache
    state_code = "nm"
    cache_key = f"{state_code}/Rapid-Response.html"
    cache.write(cache_key, html)

    # Parse out the PDF links
    document = BeautifulSoup(html, "html.parser")
    links = document.find_all("a")
    pdf_urls = [
        f"{base_url}{link['href']}"
        for link in links
        if "WARN" in link.get("href", "") and link.get("href", "").endswith(".pdf")
    ]

    output_rows = []

    for pdf_index, pdf_url in enumerate(pdf_urls):
        file_name = os.path.basename(pdf_url)
        cache_key = f"{state_code}/{file_name}"
        year = _extract_year(file_name)
        current_year = datetime.now().year
        if cache.exists(cache_key) and year is not None and year < current_year - 1:
            pdf_path = Path(cache_dir, cache_key)
        else:
            pdf_path = cache.download(cache_key, pdf_url)

        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages):
                rows = page.extract_table()

                # Loop through the rows
                for row_index, row in enumerate(rows):
                    # Skip headers on all but first page of first PDF
                    if pdf_index > 0 and row_index == 0:
                        logger.debug(
                            f"Skipping header row on PDF {pdf_index+1} page {page_index+1}"
                        )
                        continue

                    # Extract data
                    output_row = [_clean_text(cell) for cell in row]

                    # Write row
                    if any([cell != "" for cell in output_row]):
                        output_rows.append(output_row)

    # Write out to CSV
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path
    return data_path


def _clean_text(text: str) -> str:
    """
    Clean up text from a PDF cell.

    Keyword arguments:
    text -- the text to clean

    Returns: the cleaned text
    """
    # Replace None with an empty string
    if text is None:
        return ""

    # Standardize whitespace
    return re.sub(r"\s+", " ", text)


def _extract_year(text: str) -> Optional[int]:
    """
    Extract the year from a string.

    Keyword arguments:
    text -- the string to extract the year from

    Returns: the year
    """
    match = re.search(r"\d{4}", text)

    if match is not None:
        return int(match.group(0))

    return None


if __name__ == "__main__":
    scrape()
