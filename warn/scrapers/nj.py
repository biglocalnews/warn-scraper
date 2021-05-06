import csv
import logging
import requests
import time

import pandas as pd

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):
    
    logger  = logging.getLogger(__name__)
    output_csv = '{}/newjersey_warn_raw.csv'.format(output_dir)

    url_main = 'http://lwd.state.nj.us/WorkForceDirectory/warn.jsp'

    page = requests.get(url_main)

    logger.info(page.status_code) # should be 200

    soup = BeautifulSoup(page.text, 'html.parser')

    tables = soup.find_all('table') # output is list-type
    logger.info(len(tables))

    # find header
    first_row = tables[0].find_all('tr')[0]
    logger.info(f'this is the first row: {first_row}')
    headers = first_row.find_all('td')
    logger.info(f'these are the headers: {headers}')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    output_header
    logger.info(f'these are the output headers: {output_header}')

    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
    tables.pop(0)
    logger.info(f'these are the tables: {tables}')

    # save rest of rows
    for table in tables:
        time.sleep(.5)
        row = table.find_all('tr')[0]
        row_contents = row.find_all('td')
        
        output_row = []
        for content in row_contents:
            output_row.append(content.text)
        output_row = [x.strip() for x in output_row]
        logger.info(f'an output_row from the table in tables loop: {output_row}')
        
        with open(output_csv, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(output_row)


    years = range(2010, 2003, -1)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # save 2010-2004
    for year in years:
        for month in months:
            url = 'https://www.nj.gov/labor/lwdhome/warn/{}/{}{}Warn.html'.format(year, month, year)

            page = requests.get(url)

            logger.info(page.status_code) # should be 200
            logger.info(url)

            soup = BeautifulSoup(page.text, 'html.parser')
        
            table = soup.find_all('table') # output is list-type
            logger.info(len(table))
            
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

    
    df = pd.read_csv(output_csv, keep_default_na = False)
    df.shape

    df.drop_duplicates(inplace = True, keep = 'first')
    df.shape

    df.to_csv(output_csv, index = False)


if __name__ == '__main__':
    scrape()
