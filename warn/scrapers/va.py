import csv
import logging
import requests

from bs4 import BeautifulSoup


logger  = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/va.csv'
    url = 'https://www.vec.virginia.gov/warn-notices'
    response = requests.get(url)
    logger.debug(f"Page status is {response.status_code} for {url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table')
    # get link to the last page
    last_page = soup.find('li', class_='pager-last').a['href']
    # slice off the number of pages
    last_page_num = int(last_page[-2:])
    # save the sub url that goes to each page
    sub_url = last_page[0:-2]
    # get header row
    header_row = []
    for header in table[0].find_all('th'):
        header_row.append(header.text.strip())
    header_row.insert(1, 'Address')
    # loop over each page
    output_rows = []
    for page in range(last_page_num + 1):
        base_url = url.strip('/warn-notices')
        page_url = base_url + sub_url + str(page)
        response = requests.get(page_url)
        logger.debug(f"Page status is {response.status_code} for {page_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all('table')
        # loop over table on each page to get rows
        for table_row in table[0].find_all('tr'):
            table_cells = table_row.find_all('td')
            # loop over cells for each row
            output_row = []
            for table_cell in table_cells:
                # parse company name & address
                if table_cell.a:
                    company = table_cell.a.text
                    address = table_cell.text.strip()[len(company):]
                    output_row.append(company)
                    output_row.append(address)
                else:
                    cell = table_cell.text.strip()
                    # get rid of newline character in the middle of a cell
                    if '\n' in cell:
                        cell = ' '.join(cell.splitlines())
                    output_row.append(cell)
            # this test to see if the row is blank (like the header) and goes to next row
            if not output_row:
                continue
            output_rows.append(output_row)
    # save to csv
    with open(output_csv, 'w') as out:
        writer = csv.writer(out)
        writer.writerow(header_row)
        writer.writerows(output_rows)
    return output_csv
