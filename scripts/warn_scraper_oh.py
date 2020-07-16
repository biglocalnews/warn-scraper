from os import path

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json

# spot-checked and linked-checked
# scraper looks good

def ohio():
    output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/ohio_warn_raw.csv'
    url = 'https://jfs.ohio.gov/warn/current.stm'
    page = requests.get(url, verify=False)

    page.status_code # should be 200

    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find_all('table') # output is list-type
    len(table)

    # find header
    first_row = table[1].find_all('tr')[0]
    headers = first_row.find_all('td')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    output_header

    # with open(output_csv, 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(output_header)
    #     writer.writerows(output_rows)


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
    ohio()
