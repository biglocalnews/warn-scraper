from os import path
import pandas as pd

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json

# spot-checked and linked-checked
# scraper looks good


def nebraska():
    output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/nebraska_warn_raw1.csv'
    years = range(2019, 2009, -1)

    url = 'https://dol.nebraska.gov/LayoffServices/WARNReportData/?year=2020'
    page = requests.get(url)

    print(page.status_code) # should be 200

    soup = BeautifulSoup(page.text, 'html.parser')


    table = soup.find_all('table') # output is list-type
    len(table)

    # find header
    first_row = table[0].find_all('tr')[2]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    output_header 

    # save 2020
    output_rows = []
    for table_row in table[0].find_all('tr'):    
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)
    output_rows.pop(0) # pop headers
    output_rows.pop(0) # pop headers
    output_rows.pop(0) # pop headers
   
    df = pd.DataFrame(output_rows, columns = output_header)

    # save 2019-2010
    for year in years:
        url = 'https://dol.nebraska.gov/LayoffServices/WARNReportData/?year={}'.format(year)

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
        output_rows.pop(0)
        output_rows.pop(0)
        output_rows.pop(0)
        df = df.append(output_rows)
        print(len(df))

# doesn't write out to a csv file yet - add second part of scraper below, then we can concat, then we can write out to csv

if __name__ == '__main__':
    nebraska()