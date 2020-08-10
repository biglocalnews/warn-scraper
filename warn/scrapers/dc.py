import csv
import logging
import requests 

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):

    logger  = logging.getLogger(__name__)
    output_csv = '{}/districtcolumbia_warn_raw.csv'.format(output_dir)

    url_12 = 'https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-closure%202012'
    url_13 = 'https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-updated%202013'
    url_14 = 'https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-closure%202014'
    url_15 = 'https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-2015-1'
    url_16 = 'https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-2016'
    url_17 = 'https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-2017'
    url_18 = 'https://does.dc.gov/page/industry-closings-and-layoffs-warn-notifications-0'
    url_19 = 'https://does.dc.gov/node/445852'
    url_20 = 'https://does.dc.gov/node/1468786'

    url_list = [url_12, url_13, url_14, url_15, url_16, url_17, url_18, url_19, url_20]

    # get data for headers
    page = requests.get(url_12)
    logger.info("Page status code is {}".format(page.status_code))

    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table') # output is list-type

    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]

    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
        
    # loop through for data
    for url in url_list:
        page = requests.get(url)
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
        
        with open(output_csv, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)

    logger.info("DC successfully scraped.")

if __name__ == '__main__':
    scrape()