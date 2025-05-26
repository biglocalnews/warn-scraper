import logging
from pathlib import Path

from .. import utils
from ..cache import Cache

# from bs4 import BeautifulSoup
# from openpyxl import load_workbook


__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212", "palewire", "stucka"]
__tags__ = ["historical", "excel", "html"]
__source__ = {
    "name": "New York Department of Labor",
    "url": "https://dol.ny.gov/warn-notices",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from New York.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)

    """
    In 2025 New York shifte from a collection of Excel and HTML to something in Tableau. Tableau notes:
    Find a new landing page for a data page, now done in Tableau: https://dol.ny.gov/warn-dashboard
    Scroll down and there's a "View in Tableau Public" I don't remember clicking
    Opens in new tab at https://public.tableau.com/app/profile/kylee.teague2482/viz/WorkerAdjustmentRetrainingNotificationWARN/WARN
    Append .csv to the end of that URL:
    https://public.tableau.com/app/profile/kylee.teague2482/viz/WorkerAdjustmentRetrainingNotificationWARN/WARN.csv
    Try it in requests, no good. Try it in browser again. File downloads. Find it in the downloads section of the browser. Right-click, copy download link, try that in requests and ... it worked?
    """

    url = "https://public.tableau.com/views/WorkerAdjustmentRetrainingNotificationWARN/WARN.csv?%3Adisplay_static_image=y&%3AbootstrapWhenNotified=true&%3Aembed=true&%3Alanguage=en-US&:embed=y&:showVizHome=n&:apiID=host0#navType=0&navSrc=Parse"

    csv_file = "ny/tableau.csv"

    cache.download(csv_file, url)

    mydata = cache.read_csv(csv_file)

    # Set the export path
    data_path = data_dir / "ny.csv"

    # Combine and write out the file
    utils.write_rows_to_csv(data_path, mydata)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
