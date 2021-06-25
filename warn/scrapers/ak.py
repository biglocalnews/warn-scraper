import csv
import re
import requests

from bs4 import BeautifulSoup



def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/alaska_warn_raw.csv'
    url = 'https://jobs.alaska.gov/RR/WARN_notices.htm'
    page = requests.get(url)
    # Force encoding to fix dashes, apostrophes, etc. on page.text from requests reponse
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table') # output is list-type
    output_rows = []
    for table_row in table[0].find_all('tr'):
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            # Collapse newlines
            partial = re.sub(r'\n', ' ', column.text)
            # Standardize whitespace
            clean_text = re.sub(r'\s+', ' ', partial)
            output_row.append(clean_text)
        output_row = [x.strip() for x in output_row]
        if output_row == [''] or output_row[0] == '':
            continue
        output_rows.append(output_row)
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(output_rows)
    return output_csv
