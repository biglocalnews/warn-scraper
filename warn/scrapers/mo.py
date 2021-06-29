import csv
import logging
import requests

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

"""
NOTES:
- 2019 and 2020 page has duplicate data
- 2017 date format is different
- 2020 url is different from everything else
- 2021 contains an extra industry column 
"""


def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/missouri_warn_raw.csv'
    years = range(2021,2014,-1)
    url = 'https://jobs.mo.gov/warn2021'
    page = requests.get(url)
    logger.debug(f"Page status is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table')  # output is list-type
    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    # save body of 2021-2015
    for year in years:
        writeBody(year,output_csv)

    return output_csv


def writeBody(year, output_csv):
    url = 'https://jobs.mo.gov/warn{}'.format(year) if (year != 2020) else 'https://jobs.mo.gov/content/2020-missouri-warn-notices'
    page = requests.get(url)
    logger.debug(f"Page status is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table')  # output is list-type
    output_rows = []
    for table_row in table[0].find_all('tr'):
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            output_row.append(column.text.strip())
        #output_row = [x.strip() for x in output_row]
        if len(output_row)<9: # to account for the extra column
            output_row.insert(2,'')
        output_rows.append(output_row)
    output_rows.pop(len(output_rows)-1) # pop "Total" row
    output_rows.pop(0) # pop header
    if len(output_rows) > 0:
        with open(output_csv, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)
