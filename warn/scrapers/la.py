import os
import logging
import re
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["pdf"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Lousiana.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)

    state_code = "la"
    base_url = "https://www.laworks.net/"
    url = f"{base_url}Downloads/Downloads_WFD.asp"

    cache_key = f"{state_code}/Downloads_WFD.html"

    page = utils.get_url(url)
    html = page.text

    cache.write(cache_key, html)

    document = BeautifulSoup(html, "html.parser")
    links = document.find_all("a")

    pdf_urls = [
        f"{base_url}{link['href']}" for link in links if "WARN Notices" in link.text
    ]

    output_rows = []

    for pdf_index, pdf_url in enumerate(pdf_urls):
        file_name = os.path.basename(pdf_url)
        cache_key = f"{state_code}/{file_name}"

        pdf_path = cache.download(cache_key, pdf_url)

        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages):
                rows = page.extract_table()

                for row_index, row in enumerate(rows):
                    output_row = [_clean_text(cell) for cell in row]

                    # Skip headers on all but first page of first PDF
                    if (pdf_index == 0 and page_index == 0) or row_index != 0:
                        output_rows.append(output_row)

    # Patch in missing header value
    output_rows[0][3] = "Employees Affected"

    data_path = Path(data_dir, f"{state_code}.csv")
    utils.write_rows_to_csv(output_rows, data_path)

    return data_path


def _clean_text(text: str) -> str:
    """
    Clean up text from a PDF cell.

    Keyword arguments:
    text -- the text to clean

    Returns: the cleaned text
    """
    if text is None:
        return ""
    # Standardize whitespace
    return re.sub(r"\s+", " ", text)


if __name__ == "__main__":
    scrape()
