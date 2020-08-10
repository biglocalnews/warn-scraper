import csv
import logging
import requests

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):

    logger = logging.getLogger(__name__)
    output_csv = '{}/maryland_warn_raw.csv'.format(output_dir)
    # max_entries = 378 # manually inserted
    years = range(2019, 2009, -1)

    url = 'http://www.dllr.state.md.us/employment/warn.shtml'
    page = requests.get(url)

    logger.info("Page status code is {}".format(page.status_code))

    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table') # output is list-type
    
    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('td')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]

    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)


    # save 2020
    output_rows = []
    for table_row in table[0].find_all('tr'):    
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

    # save 2019-2010
    for year in years:
        url = 'http://www.dllr.state.md.us/employment/warn{}.shtml'.format(year)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find_all('table') # output is list-type
        
        output_rows = []
        for table_row in table[0].find_all('tr'):    
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

    logger.info("MD successfully scraped.")

if __name__ == '__main__':
    scrape()