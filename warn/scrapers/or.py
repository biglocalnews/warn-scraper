import logging
from pathlib import Path

from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212"]
__tags__ = ["historical", "excel"]
__source__ = {
    "name": "Oregon Higher Education Coordinating Commission",
    "url": "https://ccwd.hecc.oregon.gov/Layoff/WARN",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Oregon.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Request the page and save it to the cache
    url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/or_historical.xlsx"
    )
    cache = Cache(cache_dir)
    excel_path = cache.download("or/source.xlsx", url)

    # Open it up
    workbook = load_workbook(filename=excel_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    # Convert the sheet to a list of lists
    row_list = []
    # Skip the first two rows, which contain a crufty header
    for r in list(worksheet.rows)[2:]:
        column = [cell.value for cell in r]
        row_list.append(column)

    # Set the export path
    data_path = data_dir / "or.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
