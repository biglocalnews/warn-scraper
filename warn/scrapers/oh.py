import csv
import logging
import requests

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):

    logger = logging.getLogger(__name__)
    output_csv = '{}/ohio_warn_raw.csv'.format(output_dir)
    url = 'https://jfs.ohio.gov/warn/current.stm'
    page = requests.get(url, verify=False)

    logger.info("Page status code is {}".format(page.status_code))
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table') # output is list-type
   
    # find header
    first_row = table[1].find_all('tr')[0]
    headers = first_row.find_all('td')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]

    # if len(table) == 1:
    output_rows = []
    for table_row in table[1].find_all('tr'):    
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)
    # remove first empty row
    output_rows.pop(0)

    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
        writer.writerows(output_rows)


if __name__ == '__main__':
    scrape()
