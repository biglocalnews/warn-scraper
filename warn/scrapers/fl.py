import csv
import logging
import requests
import urllib3

from bs4 import BeautifulSoup

from warn.utils import write_rows_to_csv

logger  = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = '{}/florida_warn_raw.csv'.format(output_dir)
    # max_entries = 378 # manually inserted
    # start_row_list = range(1, max_entries, 50)
    years = ['2019', '2020', '2021']
    # Load for first time => get header
    year = 2020
    page = 1
    html = scrape_page(year, page)
    soup = BeautifulSoup(html, 'html.parser')
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
    write_rows_to_csv(output_rows, output_csv)

    # NB: still fails to capture all information
    # e.g. gets Macy's but not store address, 
    # layoff date skips "thru 03-30-20"
    # in fact, that text isnt captured by any html
    # am i reading it in poorly? is beautiful soup reading it in wrong?
    # html5lib works. what's different between html5lib and html.parser
    for year in years:
        if year == '2020':
            pages = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
        elif year == '2019':
            pages = [1,2,3,4]
        for page in pages:
            html = scrape_page(year, page)
            soup = BeautifulSoup(html, 'html5lib')
            table = soup.find_all('table')
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

            with open(output_csv, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)
    return output_csv

def scrape_page(year, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    url = f'https://reactwarn.floridajobs.org/WarnList/Records?year={year}&page={page}'
    # FL site requires realistic User-Agent. Also sidestep SSL error
    urllib3.disable_warnings()
    response = requests.get(url, headers=headers, verify=False)
    logger.debug(f"Request status is {response.status_code} for {url}")
    return response.text
