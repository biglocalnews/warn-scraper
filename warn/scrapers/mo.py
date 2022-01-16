import csv
import typing
import logging
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Missouri.

    NOTES for data cleaning:
    - 2019 and 2020 page has duplicate data
    - 2017 date format is different

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "mo.csv"
    raw_csv = f"{cache_dir}/mo_raw.csv"
    years = range(2021, 2014, -1)
    url = "https://jobs.mo.gov/warn2021"

    page = utils.get_url(url)
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
    with open(raw_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    # save body of 2021-2015
    for year in years:
        _write_body(year, output_csv)
        _write_body(year, raw_csv)

    _dedupe(output_csv)
    return output_csv


def _write_body(year, output_csv):
    # 2020 has a different link structure
    url = (
        f"https://jobs.mo.gov/warn{year}"
        if (year != 2020)
        else "https://jobs.mo.gov/content/2020-missouri-warn-notices"
    )
    page = utils.get_url(url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
    output_rows = []
    for table_row in table[0].find_all("tr"):
        columns = table_row.find_all("td")
        output_row = []
        for column in columns:
            output_row.append(column.text.strip())
        if len(output_row) < 9:  # to account for the extra column in 2021
            output_row.insert(2, "")
        if "raw" not in str(output_csv):
            if (
                year == 2019 and "2020" in output_row[0]
            ):  # account for duplicated 2020 data
                continue
        output_rows.append(output_row)
    output_rows.pop(len(output_rows) - 1)  # pop "Total" row
    output_rows.pop(0)  # pop header
    if len(output_rows) > 0:
        utils.write_rows_to_csv(output_rows, output_csv, mode="a")


def _dedupe(output_csv):
    df = pd.read_csv(output_csv, keep_default_na=False)
    df.drop_duplicates(inplace=True, keep="first")
    df.to_csv(output_csv, index=False)
    return output_csv


if __name__ == "__main__":
    scrape()
