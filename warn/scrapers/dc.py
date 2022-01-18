import csv
import typing
import logging
from pathlib import Path

from bs4 import BeautifulSoup
from datetime import datetime

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Washington D.C.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "dc.csv"
    url = f"https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-{datetime.today().year}"
    url_14 = "https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-closure%202014"

    # get data for headers
    page = utils.get_url(url)
    logger.debug(f"Page status code is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
    # find header
    first_row = table[0].find_all("tr")[0]
    headers = first_row.find_all("th")
    output_header = []
    for header in headers:
        output_header.append(header.text.strip())
    # save header
    with open(output_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    # build a list from href on the current page
    table_div = soup.find_all("div", {"class": "field-items"})
    # making a set bc 2014 and 2018 links are the same
    url_list = list(
        set([url, url_14] + [li.find("a")["href"] for li in table_div[1].select("li")])
    )

    for url in url_list:
        page = utils.get_url(url)
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.find_all("table")  # output is list-type
        output_rows = []
        for table_row in table[0].find_all("tr"):
            columns = table_row.find_all("td")
            output_row = []
            for column in columns:
                output_row.append(column.text.strip())
            # account for specific rows that we don't want
            if not output_row or output_row[0] == "" or output_row[0] == "Notice Date":
                continue
            output_rows.append(output_row)

        utils.write_rows_to_csv(output_rows, output_csv, mode="a")
    return output_csv


if __name__ == "__main__":
    scrape()
