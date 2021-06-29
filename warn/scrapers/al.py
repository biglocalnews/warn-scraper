import csv
from datetime import date
import requests

from bs4 import BeautifulSoup

from warn.utils import write_rows_to_csv

def scrape(output_dir, cache_dir=None):
    output_csv = '{}/alabama_warn_raw.csv'.format(output_dir)
    url = 'https://www.madeinalabama.com/warn-list/'
    page = requests.get(url)
    # can't see 2020 listings when I open web page, but they are on the summary in the google search
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
    # remove first empty row
    output_rows.pop(0)

    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    # add header to the top of the output file
    output_rows.insert(0,output_header)

    #remove the last 8 rows of dirty data
    for x in range(8): output_rows.pop()

    write_rows_to_csv(output_rows, output_csv)
    return output_csv

