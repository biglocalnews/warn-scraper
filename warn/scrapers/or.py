import csv
import logging
import requests

from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

from warn.utils import download_file

logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    # commenting out the old strategy because the historical document
    # has (different!) higher-quality data
    # output_csv = scrape_website(output_dir, cache_dir)
    output_csv = f"{output_dir}/or.csv"
    output_df = scrape_historical(cache_dir)
    output_csv = output_df.to_csv(output_csv, index=False)
    return output_csv


# download the historical data from the cloud
def scrape_historical(cache_dir):
    data_url = (
        "https://storage.googleapis.com/bln-data-public/warn-layoffs/or_historical.xlsx"
    )
    cache_key_historical = Path(cache_dir, "or")
    cache_key_historical.mkdir(parents=True, exist_ok=True)
    cache_key_historical = f"{cache_key_historical}/historical.xlsx"
    historical_df = pd.DataFrame()
    # we skip the first 2 rows of the OR historical excel
    try:
        logger.debug(f"Trying to read file {cache_key_historical} from cache...")
        historical_df = pd.read_excel(
            cache_key_historical, skiprows=2, engine="openpyxl"
        )
    except FileNotFoundError:
        logger.debug(
            f"Historical file not found in cache. Downloading to cache from {data_url}..."
        )
        file_path = download_file(data_url, cache_key_historical)
        historical_df = pd.read_excel(file_path, skiprows=2, engine="openpyxl")
    return historical_df


# spot-check once more


"""
Made while loop where page is < 50. Need to check periodically to make sure the data hasn't reached page 55.
It should be a while, as we are currently on page 44 (5/5/2020).
"""


def scrape_website(output_dir, cache_dir=None):
    # page range needs to be updated from 55 when there are enough notices for an additional page
    # as of 5/5/2020, this version of the scraper is fine
    output_csv = f"{output_dir}/or.csv"
    # pages = range(1, 44, 1)
    pages = 1
    url = "https://ccwd.hecc.oregon.gov/Layoff/WARN?page=1"
    page = requests.get(url)
    logger.debug(f"Page status is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
    # find header
    first_row = table[3].find_all("tr")[0]
    headers = first_row.find_all("th")
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    # save header
    with open(output_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
    # save pages 1-43
    while pages != 55:
        try:
            # for page_number in pages:
            url = "https://ccwd.hecc.oregon.gov/Layoff/WARN?page={}".format(pages)
            page = requests.get(url)
            logger.debug(f"Page status is {page.status_code} for {url}")
            soup = BeautifulSoup(page.text, "html.parser")
            table = soup.find_all("table")  # output is list-type
            output_rows = []
            for table_row in table[3].find_all("tr"):
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
            pages += 1
        except Exception:
            break
    return output_csv
