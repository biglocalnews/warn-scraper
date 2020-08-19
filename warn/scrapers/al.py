import csv
import logging
import requests 

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):

    logger = logging.getLogger(__name__)
    output_csv = '{}/alabama_warn_raw.csv'.format(output_dir)
    # url = 'https://www.madeinalabama.com/warn-list/'
    url = 'https://www.madeinalabama.com/warn-listz/'
    page = requests.get(url)

    # can't see 2020 listings when I open web page, but they are on the summary in the google search

    logger.info("Page status code is {}".format(page.status_code))

    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find_all('table') # output is list-type

    # if len(table) == 1:
    output_rows = []
    for table_row in table[0].find_all('tr'):    
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)
    # remove first empty row
    output_rows.pop(0)

    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    output_header

    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
        writer.writerows(output_rows)

    logger.info("AL successfully scraped.")

if __name__ == '__main__':
    scrape()

