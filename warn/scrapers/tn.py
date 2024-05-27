import csv
import typing
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["anikasikka", "stucka"]
__tags__ = ["html"]
__source__ = {
    "name": "Tennessee Department of Labor and Workforce Development",
    "url": "https://www.tn.gov/workforce/general-resources/major-publications0/major-publications-redirect/reports.html",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Tennessee.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Initialize the cache
    cache = Cache(cache_dir)

    # Grab the HTML page with the latest years of data
    page = utils.get_url(
        "https://www.tn.gov/workforce/general-resources/major-publications0/major-publications-redirect/reports.html"
    )
    html = page.text
    cache.write("tn/source.html", html)
    soup = BeautifulSoup(html, "html5lib")
    tables = soup.find_all(attrs={"class": "tn-datatable"})
    rows = BeautifulSoup(str(tables), "html5lib").find_all("tr")

    dataheaders: typing.List = [
        "Notice Date",
        "Effective Date",
        "Received Date",
        "Company",
        "City",
        "County",
        "No. Of Employees",
        "Layoff/Closure",
        "Notice ID",
        # "Notice URL",
    ]

    staginglist: typing.List = []
    for row in reversed(rows):
        cells = row.find_all("td")
        if len(cells) == 6:  # Filter for potentially valid rows
            line: typing.Dict = {}
            for item in dataheaders:  # Build an ordered dictionary with null values
                line[item] = None
            line["Notice Date"] = cells[0].text.strip()
            line["Effective Date"] = cells[4].text.strip()
            line["Company"] = cells[1].text.strip()
            line["County"] = cells[2].text.strip()
            line["No. Of Employees"] = cells[3].text.strip()
            line["Notice ID"] = cells[5].text.strip()
            # line['Notice URL'] = cells[1].find("a")['href']
            staginglist.append(line)

    # Bring in historical data
    historical_file = cache_dir / "tn/tn_historical.csv"
    historical_url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/tn_historical.csv"
    )
    utils.fetch_if_not_cached(historical_file, historical_url)
    historical_str = cache.read("tn/tn_historical.csv")

    historicallist = list(csv.DictReader(historical_str.splitlines()))

    # Combine fresh and historical
    staginglist.extend(historicallist)

    output_csv = data_dir / "tn.csv"

    utils.write_dict_rows_to_csv(output_csv, dataheaders, staginglist)

    return output_csv


if __name__ == "__main__":
    scrape()
