import os
import logging
import requests
import pandas as pd

def scrape(output_dir):

    logger  = logging.getLogger(__name__)

    url = 'https://wsd.dli.mt.gov/_docs/wioa/warn.xlsx'
    df = pd.read_excel(url)
    output_file = '{}/montana_warn_raw.csv'.format(output_dir)
    df.to_csv(output_file, index=False)

if __name__ == '__main__':
    scrape()