import csv
import typing
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Utah.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "ut.csv"
    url = "https://jobs.utah.gov/employer/business/warnnotices.html"
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")
    tables = soup.find_all("table")  # output is list-type
    # find header
    first_row = tables[0].find_all("tr")[0]
    headers = first_row.find_all("th")
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    output_header
    # save header
    with open(output_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
    for table in tables:
        output_rows = []
        for table_row in table.find_all("tr"):
            columns = table_row.find_all("td")
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_row = [x.strip() for x in output_row]
            output_rows.append(output_row)
        output_rows.pop(0)
        if len(output_rows) > 0:
            with open(output_csv, "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)
    return output_csv


if __name__ == "__main__":
    scrape()
