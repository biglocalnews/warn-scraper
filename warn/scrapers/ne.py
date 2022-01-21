import csv
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = ["html"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Nebraska.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = cache_dir / "ne" / "raw1.csv"
    utils.create_directory(output_csv, is_file=True)
    years = range(2019, 2009, -1)
    url = "https://dol.nebraska.gov/LayoffServices/WARNReportData/?year=2020"
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
    # find header
    first_row = table[0].find_all("tr")[2]
    headers = first_row.find_all("th")
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    # save header
    with open(output_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
    # save 2020
    output_rows = []
    for table_row in table[0].find_all("tr"):
        columns = table_row.find_all("td")
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)
    output_rows.pop(0)  # pop headers
    output_rows.pop(0)  # pop headers
    output_rows.pop(0)  # pop headers
    if len(output_rows) > 0:
        with open(output_csv, "a") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)
    # save 2019-2010
    for year in years:
        url = "https://dol.nebraska.gov/LayoffServices/WARNReportData/?year={}".format(
            year
        )
        page = utils.get_url(url)
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.find_all("table")  # output is list-type
        output_rows = []
        for table_row in table[0].find_all("tr"):
            columns = table_row.find_all("td")
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_row = [x.strip() for x in output_row]
            output_rows.append(output_row)
        output_rows.pop(0)
        output_rows.pop(0)
        output_rows.pop(0)
        if len(output_rows) > 0:
            with open(output_csv, "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)
    _nebraska_two(cache_dir)

    # Read in the two CSVs
    cache = Cache(cache_dir)
    row_list = []
    for i, f in enumerate(["ne/raw1.csv", "ne/raw2.csv"]):
        # Read in the file
        data = cache.read_csv(f)

        # Cut the header from everything after the first file
        if i > 0:
            data = data[1:]

        # Add it to the combined list
        row_list.extend(data)

    # Write them out
    output_csv = data_dir / "ne.csv"
    utils.write_rows_to_csv(row_list, output_csv)

    # Return the path
    return output_csv


def _nebraska_two(cache_dir):
    output_csv = cache_dir / "ne" / "raw2.csv"
    utils.create_directory(output_csv, is_file=True)
    years = range(2019, 2009, -1)
    url = (
        "https://dol.nebraska.gov/LayoffServices/LayoffAndClosureReportData/?year=2020"
    )
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
    # find header
    first_row = table[0].find_all("tr")[2]
    headers = first_row.find_all("th")
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    # save header
    with open(output_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
    # save 2020
    output_rows = []
    for table_row in table[0].find_all("tr"):
        columns = table_row.find_all("td")
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)
    output_rows.pop(0)  # pop headers
    output_rows.pop(0)  # pop headers
    output_rows.pop(0)  # pop headers
    if len(output_rows) > 0:
        with open(output_csv, "a") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)
    # save 2019-2010
    for year in years:
        url = "https://dol.nebraska.gov/LayoffServices/LayoffAndClosureReportData/?year={}".format(
            year
        )
        page = utils.get_url(url)
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.find_all("table")  # output is list-type
        output_rows = []
        for table_row in table[0].find_all("tr"):
            columns = table_row.find_all("td")
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_row = [x.strip() for x in output_row]
            output_rows.append(output_row)
        output_rows.pop(0)
        output_rows.pop(0)
        if len(output_rows) > 0:
            output_rows.pop(0)
        if len(output_rows) > 0:
            with open(output_csv, "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)
    return output_csv


if __name__ == "__main__":
    scrape()
