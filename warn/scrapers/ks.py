import csv
import logging
import requests
import pandas as pd

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):

    logger = logging.getLogger(__name__)
    
    output_csv = '{}/kansas_warn_raw.csv'.format(output_dir)
    max_entries = 950 # manually inserted
    # script should be checked periodically to make sure the entries are below 550 - otherwise, there will be missing info
    start_row_list = range(1, max_entries, 25)

    # Load for first time => get header
    start_row = 1
    url = 'https://www.kansasworks.com/ada/mn_warn_dsp.cfm?securitysys=on&start_row={}&max_rows=25&orderby=employer&choice=1'.format(start_row)
    page = requests.get(url)

    logger.info("Page status code is {}".format(page.status_code))

    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find_all('table') # output is list-type
    len(table)

    # find header
    first_row = table[1].find_all('tr')[0]
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

    for start_row in start_row_list:
        try:
            url = 'https://www.kansasworks.com/ada/mn_warn_dsp.cfm?securitysys=on&start_row={}&max_rows=25&orderby=employer&choice=1'.format(start_row)

            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            table = soup.find_all('table') # output is list-type

            output_rows = []
            for table_row in table[1].find_all('tr'):    
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

        except IndexError:
            logger.info(url + ' not found')

    add_links_ks(logger)
    add_affected_ks(logger)


def add_links_ks(logger):

    output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/kansas_warn_raw.csv'
    max_entries = 950 # manually inserted
    start_row_list = range(1, max_entries, 25)

    # Load for first time => get header
    pd.options.display.max_rows = 999
    pd.options.display.max_columns = 99
    start_row = 1
    links = []
    for start_row in start_row_list:
        try:
            url = 'https://www.kansasworks.com/ada/mn_warn_dsp.cfm?securitysys=on&start_row={}&max_rows=25&orderby=employer&choice=1'.format(start_row)
            page = requests.get(url)

            soup = BeautifulSoup(page.text, 'html.parser')

            table = soup.find_all('table') # output is list-type
            for a in soup.find_all('a', href=True, text=True):
                link_text = a['href']
    
                if 'callingfile' in link_text:
                    links.append(link_text)

        except IndexError:
            logger.info(url + ' not found')

    data = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/kansas_warn_raw.csv')
    data['url_suffix'] = links
    data['Employer Name'] = data['Employer'].str.replace('\r', '')
    data['City'] = data['City'].str.replace('\r', '')
    data.drop(columns='Employer', inplace=True)
    data = data[['url_suffix', 'Employer Name', 'City', 'Zip', 'LWIB Area', 'Notice Date']]
    data.to_csv(output_csv)

def add_affected_ks(logger):

    ks_data = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/kansas_warn_raw.csv')
    base_url = 'https://www.kansasworks.com/ada/'

    full_url_list = []
    for url_suffix in ks_data['url_suffix']:
        full_url = base_url + url_suffix
        full_url_list.append(full_url)

    employees_affected = [['URL','Affected Employees']]
    for url in full_url_list:
        logger.info('scraper is on {}'.format(url))
        
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find('table') # output is list-type
    
        rows = table.find_all('tr')
        for row in rows:
            if 'employees' in row.text:
                data = row.find_all('td')
                affected_num = data[1].get_text()
                affected_num = affected_num.replace(u'\xa0', u'')
                if 'Company' in affected_num:
                    company = 'doing nothing'
                else:
                    keep_data = [url, affected_num]
                    employees_affected.append(keep_data)

    headers = employees_affected.pop(0)
    df = pd.DataFrame(employees_affected, columns=headers)
    df['Suffix'] = df['URL'].str.split('/ada/').str[-1]

    df = df.drop_duplicates(subset='URL', keep="first")
    all_ks_data = pd.merge(ks_data, df, left_on='url_suffix', right_on='Suffix')
    all_ks_data.drop(columns=['Unnamed: 0','Suffix', 'url_suffix'], inplace=True)
    all_ks_data.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/kansas_warn_raw.csv')

    logger.info("KS successfully scraped.")

if __name__ == '__main__':
    scrape()