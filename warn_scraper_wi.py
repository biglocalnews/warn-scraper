from os import path
import pathlib

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json

import re

# spot-checked and linked-checked
# scraper looks good
root = pathlib.Path(__file__).parent.resolve()
# run action again

def wisconsin():
    output_csv = root / 'data' / 'wisconsin_warn_raw.csv'
    #output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/wisconsin_warn_raw.csv'
    years = [2016, 2017, 2018, 2019]

    url = 'https://sheets.googleapis.com/v4/spreadsheets/1cyZiHZcepBI7ShB3dMcRprUFRG24lbwEnEDRBMhAqsA/values/Originals?key=AIzaSyDP0OltIjcmRQ6-9TTmEVDZPIX6BSFcunw'
    response = requests.get(url)
    print(response.status_code)

    data = response.json()

    # find header
    headers = data['values'][0]
    output_header = headers[3:len(headers)-1]

    output_header

    output_rows = []
    for row in data['values'][1:len(data['values'])]:
        output_row = row[3:len(row)]
        output_rows.append(output_row)


    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
        writer.writerows(output_rows)


    for year in years:
        url = 'https://dwd.wisconsin.gov/dislocatedworker/warn/{}/default.htm'.format(year)
        page = requests.get(url)

        print(page.status_code) # should be 200

        soup = BeautifulSoup(page.text, 'html.parser')
        
        tables = soup.find_all('table') # output is list-type
        print(len(tables))
        
        for table in tables:
            output_rows = []
            for table_row in table.find_all('tr'):    
                columns = table_row.find_all('td')
                output_row = []
                for column in columns:
                    entry = column.text
                    # remove trailing characters after LayoffBeginDate
                    if re.match(r"^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", entry):
                        entry = re.sub(r"(?<=[0-9]{4}).*", "", entry)
                    output_row.append(entry)
                output_row = [x.strip() for x in output_row]
                # filter "Updates to Previously Filed Notices"
                if len(output_row) != 9:
                    print(output_row)
                else:
                    output_rows.append(output_row)
                    
            if len(output_rows) > 0:
                with open(output_csv, 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(output_rows)


if __name__ == '__main__':
    wisconsin()
