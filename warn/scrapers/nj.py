import logging
from pathlib import Path

from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "palewire"]
__tags__ = ["html"]
__source__ = {
    "name": "New Jersey Department of Labor and Workforce Development",
    "url": "https://www.nj.gov/labor/employer-services/warn/",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from New Jersey.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Fire up the cache
    cache = Cache(cache_dir)

    # Download URL
    url = "https://www.nj.gov/labor/assets/PDFs/WARN/WARN_Notice_Archive.xlsx"
    wb_path = cache.download("nj/source.xlsx", url)

    # Read in the workbook
    output_rows = []
    wb = load_workbook(filename=wb_path)
    for ws in wb.worksheets:
        logger.debug(f"Parsing {ws}")
        for i, row in enumerate(ws.rows):

            # Skip header
            if i == 0:
                continue

            # A list with only empty cells will throw an error
            try:
                next(v for v in row if v.value)
            except StopIteration:
                continue

            # Parse out data
            d = {
                "Company": _parse_value(row[0]),
                "City": _parse_value(row[1]),
                "Month Posted": _parse_value(row[2]),
                "Effective Date": _parse_value(row[3]),
                "Workforce Affected": _parse_value(row[4]),
            }

            # Tack it on
            output_rows.append(d)

    # Set the export path
    data_path = data_dir / "nj.csv"

    # Write out the file
    headers = output_rows[0].keys()
    utils.write_dict_rows_to_csv(data_path, headers, output_rows)

    # Return the path to the file
    return data_path


def _parse_value(cell):
    v = cell.value
    if isinstance(v, str):
        return v.strip()
    return v


if __name__ == "__main__":
    scrape()
