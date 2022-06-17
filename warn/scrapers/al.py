import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = [
    "html",
]
__source__ = {
    "name": "Alabama Department of Commerce",
    "url": "https://www.madeinalabama.com/warn-list/",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Alabama.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "al.csv"
    page = utils.get_url("https://www.madeinalabama.com/warn-list/")
    # can't see 2020 listings when I open web page, but they are on the summary in the google search
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
    table_rows = table[0].find_all("tr")
    # Handle the header
    raw_header = table_rows.pop(0)
    header_row = _extract_fields_from_row(raw_header, "th")
    output_rows = [header_row]
    # Process remaining rows
    discarded_rows = []
    for table_row in table_rows:
        # Discard bogus data lines (see last lines of source data)
        # based on check of first field ("Closing or Layoff")
        data = _extract_fields_from_row(table_row, "td")
        layoff_type = data[0]
        if re.match(r"(clos|lay)", layoff_type, re.I):
            output_rows.append(data)
        else:
            discarded_rows.append(data)
    if discarded_rows:
        logger.warn(f"Warning: Discarded {len(discarded_rows)} dirty data row(s)")
    utils.write_rows_to_csv(output_csv, output_rows)
    return output_csv


def _extract_fields_from_row(row, element):
    """Pluck data from the provided row and element."""
    row_data = []
    fields = row.find_all(element)
    for raw_field in fields:
        field = raw_field.text.strip()
        row_data.append(field)
    return row_data


if __name__ == "__main__":
    scrape()
