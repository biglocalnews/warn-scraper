import csv
import logging
import requests

from bs4 import BeautifulSoup

# spot-check once more

"""
Made while loop where page is < 50. Need to check periodically to make sure the data hasn't reached page 55.
It should be a while, as we are currently on page 44 (5/5/2020).
"""

logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    # page range needs to be updated from 55 when there are enough notices for an additional page
    # as of 5/5/2020, this version of the scraper is fine
    output_csv = f'{output_dir}/oregon_warn_raw.csv'
    # pages = range(1, 44, 1)
    pages = 1
    url = 'https://ccwd.hecc.oregon.gov/Layoff/WARN?page=1'
    page = requests.get(url)
    logger.info("Page status code is {}".format(page.status_code))
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table') # output is list-type
    # find header
    first_row = table[3].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
    # save pages 1-43
    while pages != 55:
        try:
    # for page_number in pages:
            url = 'https://ccwd.hecc.oregon.gov/Layoff/WARN?page={}'.format(pages)
            page = requests.get(url)
            logger.debug(f"Page status is {page.status_code} for {url}")
            soup = BeautifulSoup(page.text, 'html.parser')
            table = soup.find_all('table') # output is list-type
            output_rows = []
            for table_row in table[3].find_all('tr'):
                columns = table_row.find_all('td')
                output_row = []
                for column in columns:
                    output_row.append(column.text)
                output_row = [x.strip() for x in output_row]
                output_rows.append(output_row)
            output_rows.pop(0)
            if len(output_rows) > 0:
                with open(output_csv, 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(output_rows)
            pages += 1
        except:
            break
    return output_csv
