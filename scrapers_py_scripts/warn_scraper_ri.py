from os import path

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json


# spot-checked and linked-checked
# scraper looks good

def rhodeisland():
    output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/rhodeisland_warn_raw.csv'
    # url = 'http://www.dlt.ri.gov/bwc/WARN.htm'
    # page = requests.get(url)

    # page.status_code # should be 200

    # soup = BeautifulSoup(page.text, 'html.parser')

    # table = soup.find_all('table') # output is list-type
    # len(table)

    # # find header
    # first_row = table[6].find_all('tr')[1]
    # headers = first_row.find_all('td')
    # output_header = []
    # for header in headers:
    #     output_header.append(header.text)
    # # output_header = [x.strip().replace("\r\n","").replace("\s", "") for x in output_header]
    # output_header = [' '.join(x.split()) for x in output_header]
    # output_header

    # # if len(table) == 1:
    # output_rows = []
    # for table_row in table[6].find_all('tr'):    
    #     columns = table_row.find_all('td')
    #     output_row = []
    #     for column in columns:
    #         output_row.append(column.text)
    #     output_row = [x.strip() for x in output_row]
    #     output_rows.append(output_row)
    # # remove first empty row
    # output_rows.pop(0)
    # output_rows.pop(0)
    # output_rows.pop(0)

    # with open(output_csv, 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(output_header)
    #     writer.writerows(output_rows)


    url = 'https://dlt.ri.gov/wds/warn/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    tables = soup.find_all('table') # output is list-type
    print(len(tables))

    first_row = tables[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    print(output_header)

    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    for table in tables:
        output_rows = []
        for table_row in table.find_all('tr'):    
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

if __name__ == '__main__':
    rhodeisland()