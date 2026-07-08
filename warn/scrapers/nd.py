import logging
import re
from pathlib import Path

import pdfplumber

from .. import utils
from ..cache import Cache

__authors__ = ["riordan"]
__tags__ = ["pdf"]
__source__ = {
    "name": "Job Service North Dakota",
    "url": "https://www.jobsnd.com/documents",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from North Dakota.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Fire up the cache
    cache = Cache(cache_dir)
    state_code = "nd"

    # North Dakota publishes a single static PDF covering 2015 to the present.
    pdf_url = "https://www.jobsnd.com/sites/www/files/documents/jsnd-documents/WARN%20Notices%202015%20to%20present.pdf"

    # Download the PDF and stash the raw file, unedited, in the cache
    cache_key = f"{state_code}/WARN_Notices_2015_to_present.pdf"
    pdf_path = cache.download(cache_key, pdf_url)

    # Loop through the PDF pages and pull out the table
    output_rows: list = []
    header_written = False
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            rows = page.extract_table() or []

            for row in rows:
                # Standardize each cell
                output_row = [_clean_text(cell) for cell in row]

                # Skip fully empty rows
                if not any(output_row):
                    continue

                # The header repeats at the top of the table. Keep it once.
                if output_row[0] == "Company Name":
                    if header_written:
                        logger.debug(
                            f"Skipping repeated header row on page {page_index + 1}"
                        )
                        continue
                    header_written = True

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

    # Collapse newlines and standardize whitespace
    return re.sub(r"\s+", " ", text).strip()


if __name__ == "__main__":
    scrape()
