import logging
import re
import requests

from bs4 import BeautifulSoup
import pandas as pd
from zipfile import BadZipFile

logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/tx.csv'
    url = 'https://www.twc.texas.gov/businesses/worker-adjustment-and-retraining-notification-warn-notices#warnNotices'
    page = requests.get(url)
    logger.debug(f"Page status is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, 'html.parser')
    # download each year's excel file
    links = soup.find_all('a', href=re.compile('^/files/news/warn-act-listings-'))
    # create empty pandas dataframe
    output_df = pd.DataFrame()
    for link in links:
        # get each url from the HTML links we found
        data_url = f'https://www.twc.texas.gov{link.get("href")}'
        logger.info(f'goign to try file {data_url}')
        # xlsx and older xls files require different engines for this pandas func
        # TODO implement cacheing check for these files
        try:
            year_df = pd.read_excel(data_url, engine='openpyxl')
        except BadZipFile:
            year_df = pd.read_excel(data_url, engine='xlrd')
        output_df = output_df.append(year_df)
    logger.debug(output_df)
    # drop empty columns
    # TODO: why arent empty cols droppin???
    output_df.dropna(inplace=True, axis=1, how='all')
    output_df.to_csv(output_csv, index=False)
    return output_csv
