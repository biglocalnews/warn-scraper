import csv
import requests

from bs4 import BeautifulSoup

# spot-check once more

"""
Made while loop where page is < 50. Need to check periodically to make sure the data hasn't reached page 55.
It should be a while, as we are currently on page 44 (5/5/2020).
"""


def scrape():

    # page range needs to be updated from 55 when there are enough notices for an additional page
    # as of 5/5/2020, this version of the scraper is fine

    output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/oregon_warn_raw.csv'
    # pages = range(1, 44, 1)
    pages = 1

    url = 'https://ccwd.hecc.oregon.gov/Layoff/WARN?page=1'
    page = requests.get(url)

    print(page.status_code) # should be 200

    soup = BeautifulSoup(page.text, 'html.parser')


    table = soup.find_all('table') # output is list-type
    len(table)

    # find header
    first_row = table[3].find_all('tr')[0]
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

    # save pages 1-43
    while pages != 55:
        try:

    # for page_number in pages:
            url = 'https://ccwd.hecc.oregon.gov/Layoff/WARN?page={}'.format(pages)
            print(url)

            page = requests.get(url)

            print(page.status_code) # should be 200

            soup = BeautifulSoup(page.text, 'html.parser')
            
            table = soup.find_all('table') # output is list-type
            print(len(table))
            
            output_rows = []
            for table_row in table[3].find_all('tr'):    
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
            pages += 1

        except:
            break


if __name__ == '__main__':
    scrape()