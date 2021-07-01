import csv
import re
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
        output_rows.append(extract_fields_from_row(table_row, 'td'))
    # remove first empty row
    output_rows.pop(0)
    # find header
    first_row = table[0].find_all('tr')[0]
    # add header to the top of the output file
    output_header = extract_fields_from_row(first_row, 'th')
    output_rows.insert(0, output_header)
    write_rows_to_csv(output_rows, output_csv)
    return output_csv

#row is a beautifulsoup row object
#element is the HTML element of the desired field
def extract_fields_from_row(row, element):
    row_data = []
    fields = row.find_all(element)
    for i in range(len(fields)):
        field = fields[i].text.strip()
        #if first field not start with "la" or "cl", skip row
        if i==0:
            if re.search(r"(?i)^la", field) == None and re.search(r"(?i)^cl", field) == None: return []
        row_data.append(field)
    return row_data
