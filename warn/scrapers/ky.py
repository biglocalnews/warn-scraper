import os
import logging
import requests
import pandas as pd

def scrape(output_dir):

    # make sure this URL works, test on other days
    logger  = logging.getLogger(__name__)

    url = 'https://kcc.ky.gov/WARN%20notices/WARN%20Notices%202021/WARN%20Notice%20Report%2003222021%20.xlsx'

    # several sheets in one excel file, will come back to

    # df = pd.read_excel(url)
    # output_file = '{}/iowa_warn_raw.csv'.format(output_dir)
    # df.to_csv(output_file, index=False)


if __name__ == '__main__':
    scrape()