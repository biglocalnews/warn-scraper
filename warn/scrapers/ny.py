import csv
import requests
import logging

from bs4 import BeautifulSoup

from warn.utils import write_rows_to_csv

logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f'{cache_dir}/ny.csv'
    url = 'https://dol.ny.gov/warn-notices'

    page = requests.get(url)
    logger.debug(f"Page status is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table')  # output is list-type

    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text.strip())
    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    output_rows = []
    for table_row in table[0].find_all('tr'):
        columns = table_row.find_all('td')
        # if len(columns)>0:
        #     pdf_url = columns[0].find('a')['href']
        #     full_url = f'https://dol.ny.gov{pdf_url}'
        #     pdf = requests.get(full_url)
        #     print(pdf.content)
        output_row = []
        for column in columns:
            output_row.append(column.text.strip())
        output_rows.append(output_row)
    output_rows.pop(0) # pop header
    if len(output_rows) > 0:
        write_rows_to_csv(output_rows,output_csv,mode='a')

    return output_csv