import re
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
    Scrape data from South Dakota.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "sd.csv"
    url = "https://dlr.sd.gov/workforce_services/businesses/warn_notices.aspx"
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
    # find header
    first_row = table[0].find_all("tr")[0]
    headers = first_row.find_all("td")
    output_header = []
    for header in headers:
        output_header.append(header.text)
    # output_header = [x.strip().replace("\r\n","").replace("\s", "") for x in output_header]
    output_header = [" ".join(x.split()) for x in output_header]
    # if len(table) == 1:
    output_rows = []
    for table_row in table[0].find_all("tr"):
        columns = table_row.find_all("td")
        output_row = []
        for column in columns:
            txt = column.text.strip()
            cleantext = re.sub(r"\s+", " ", txt)
            output_row.append(cleantext)
        output_rows.append(output_row)
    # remove first empty row
    output_rows.pop(0)
    with open(output_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
        writer.writerows(output_rows)
    return output_csv


if __name__ == "__main__":
    scrape()
