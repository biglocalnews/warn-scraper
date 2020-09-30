import csv
import logging
import requests

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):

    logger = logging.getLogger(__name__)
    output_csv = '{}/alaska_warn_raw.csv'.format(output_dir)
    # output_csv = '{}/alaska_warn_raw.csv'.format(new_dir)

    # url = 'https://jobs.alaska.gov/RR/WARN_notices.htm'
    url = 'https://jobs.alaska.gov/RR/WARN_notices.htmz'

    page = requests.get(url)
    logger.info("Page status code is {}".format(page.status_code))

    soup = BeautifulSoup(page.text, 'html.parser')
    # print(soup)

    table = soup.find_all('table') # output is list-type
    output_header = [
        'Company',
        'Location',
        'Notice Date', 
        'Layoff Date', 
        'Employees Affected', 
        'Notes'
        ]

    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    output_rows = []
    for table_row in table[0].find_all('tr'):    
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)

    # print(output_rows)
    logger.info("AK successfully scraped.")
    

    

if __name__ == '__main__':
    scrape()