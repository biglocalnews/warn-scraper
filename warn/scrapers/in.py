import csv
import logging
import requests

from bs4 import BeautifulSoup

logger  = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = '{}/indiana_warn_raw.csv'.format(output_dir)
    # max_entries = 378 # manually inserted
    # start_row_list = range(1, max_entries, 50)
    url1 = 'https://www.in.gov/dwd/2567.htm'
    page = requests.get(url1)
    logger.debug(f"Page status is {page.status_code} for {url1}")
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find_all('table') # output is list-type
    len(tables)
    # find header
    first_row = tables[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    output_header
    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
    for table in tables:
        output_rows = []
        for table_row in table.find_all('tr'):
            columns = table_row.find_all('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_row = [x.strip() for x in output_row]
            output_rows.append(output_row)
        output_rows.pop(0)
        # print(output_rows[0])
        if len(output_rows) > 0:
            with open(output_csv, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)
    url2 = 'https://www.in.gov/dwd/3125.htm'
    page = requests.get(url2)
    logger.debug(f"Page status is {page.status_code} for {url2}")
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find_all('table') # output is list-type
    len(tables)
    for table in tables:
        output_rows = []
        for table_row in table.find_all('tr'):
            columns = table_row.find_all('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_row = [x.strip() for x in output_row]
            output_rows.append(output_row)
        output_rows.pop(0)
        # print(output_rows[0])
        if len(output_rows) > 0:
            with open(output_csv, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)
    return output_csv
