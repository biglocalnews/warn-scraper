import logging
import requests

from bs4 import BeautifulSoup
import pandas as pd

logger  = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/ia.csv'
    url = 'https://www.iowaworkforcedevelopment.gov/worker-adjustment-and-retraining-notification-act'
    page = requests.get(url)
    logger.debug(f"Page status is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, 'html.parser')
    data_url = soup.find('a',{"title":"WARN Log Excel File"})['href']
    df = pd.read_excel(data_url)
    df.dropna(inplace=True, axis=1, how='all')
    df.to_csv(output_csv, index=False)
    return output_csv

