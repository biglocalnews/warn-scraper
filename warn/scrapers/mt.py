from pathlib import Path

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "ydoc5212"]
__tags__ = ["html", "excel"]
__source__ = {
    "name": "Montana Department of Labor and Industry",
    "url": "https://wsd.dli.mt.gov/wioa/related-links/warn-notice-page",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Montana.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get the URL
    url = "http://wsd.dli.mt.gov/wioa/related-links/warn-notice-page"
    r = utils.get_url(url, verify=False)
    html = r.text

    # Save it to the cache
    cache = Cache(cache_dir)
    cache.write("mt/source.html", html)

    # Parse out the Excel link
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find(id="boardPage").find_all("a")
    excel_name = [
        link.attrs["href"]
        for link in links
        if link.attrs.get("href", "").endswith(
            "xlsx"
        )  # URL will look like: ="../../_docs/wioa/warn-9-1-21.xlsx"
    ][0].split("/")[-1]
    excel_url = f"http://wsd.dli.mt.gov/_docs/wioa/{excel_name}"

    # Download the Excel file
    excel_path = cache.download("mt/source.xlsx", excel_url, verify=False)

    # Open it up
    workbook = load_workbook(filename=excel_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    # Convert the sheet to a list of lists
    row_list = []
    for row in worksheet.rows:
        # Get the cells
        cell_list = [cell.value for cell in row]

        # Skip empty rows
        try:
            # A list with only empty cell will throw an error
            next(i for i in cell_list if i)
        except StopIteration:
            continue

        # Add it to the pile
        row_list.append(cell_list)

    # Set the export path
    data_path = data_dir / "mt.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
