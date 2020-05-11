from os import path

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json

# link-checked and spot-checked, looks good

def missouri():
    output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/missouri_warn_raw.csv'
    years = range(2018, 2014, -1)

    url = 'https://jobs.mo.gov/warn2019'
    page = requests.get(url)

    print(page.status_code) # should be 200

    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find_all('table') # output is list-type
    len(table)

    # find header
    first_row = table[0].find_all('tr')[0]
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


    # save 2019
    output_rows = []
    for table_row in table[0].find_all('tr'):    
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)
    output_rows.pop(len(output_rows) - 1) # pop "Total" row
    output_rows.pop(0) # pop header

    if len(output_rows) > 0:
        with open(output_csv, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)


    # save 2018-2015
    for year in years:
        url = 'https://jobs.mo.gov/warn{}'.format(year)
        page = requests.get(url)

        print(page.status_code) # should be 200

        soup = BeautifulSoup(page.text, 'html.parser')
        
        table = soup.find_all('table') # output is list-type
        print(len(table))
        
        output_rows = []
        for table_row in table[0].find_all('tr'):    
            columns = table_row.find_all('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_row = [x.strip() for x in output_row]
            output_rows.append(output_row)
        output_rows.pop(len(output_rows)-1)
        output_rows.pop(0)

        if len(output_rows) > 0:
            with open(output_csv, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)


if __name__ == '__main__':
    missouri()