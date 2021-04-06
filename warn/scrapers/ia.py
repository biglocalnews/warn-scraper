import os
import logging
import requests
import pandas as pd

def scrape(output_dir):

    # make sure this URL works, test on other days
    logger  = logging.getLogger(__name__)

    url = 'https://www.iowaworkforcedevelopment.gov/sites/search.iowaworkforcedevelopment.gov/files/documents/2018/WARN_20210331.xlsx'

    df = pd.read_excel(url)
    output_file = '{}/iowa_warn_raw.csv'.format(output_dir)
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    scrape()