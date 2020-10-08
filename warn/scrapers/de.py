
import csv
import logging
import requests
import pandas as pd

from bs4 import BeautifulSoup

def scrape(output_dir):

    logger  = logging.getLogger(__name__)
    output_csv = '{}/delaware_warn_raw.csv'.format(output_dir)

    start_row = 1
    url = 'https://joblink.delaware.gov/ada/mn_warn_dsp.cfm?securitysys=on&start_row={}&max_rows=50&orderby=employer&choice=1'.format(start_row)
    page = requests.get(url)

    logger.info("Page status code is {}".format(page.status_code))

    soup = BeautifulSoup(page.text, 'html.parser')
    max_entries = get_total_results_count(soup)
    start_row_list = range(1, max_entries, 50)
    table = soup.find_all('table') # output is list-type

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
            url = 'https://joblink.delaware.gov/ada/mn_warn_dsp.cfm?securitysys=on&start_row={}&max_rows=50&orderby=employer&choice=1'.format(start_row)
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

    add_links_de(logger, output_dir, max_entries)
    add_affected_de(logger, output_dir)


def add_links_de(logger, output_dir, max_entries):

    output_csv = '{}/delaware_warn_raw.csv'.format(output_dir)

    start_row_list = range(1, max_entries, 50)
    start_row = 1
    links = []
    for start_row in start_row_list:
        try:
            url = 'https://joblink.delaware.gov/ada/mn_warn_dsp.cfm?securitysys=on&start_row={}&max_rows=50&orderby=employer&choice=1'.format(start_row)
            page = requests.get(url)

            soup = BeautifulSoup(page.text, 'html.parser')

            table = soup.find_all('table') # output is list-type
            for a in soup.find_all('a', href=True, text=True):
                link_text = a['href']
    
                if 'callingfile' in link_text:
                    links.append(link_text)

        except IndexError:
            logger.info(url + ' not found')

    data = pd.read_csv('{}/delaware_warn_raw.csv'.format(output_dir))
    data['url_suffix'] = links
    data['Employer Name'] = data['Employer'].str.replace('\r', '')
    data.drop(columns='Employer', inplace=True)
    data = data[['url_suffix', 'Employer Name', 'City', 'Zip', 'LWIB Area', 'Notice Date']]
    data.to_csv(output_csv)

def add_affected_de(logger, output_dir):

    de_data = pd.read_csv('{}/delaware_warn_raw.csv'.format(output_dir))
    base_url = 'https://joblink.delaware.gov/ada/'

    full_url_list = []
    for url_suffix in de_data['url_suffix']:
        full_url = base_url + url_suffix
        full_url_list.append(full_url)

    employees_affected = [['URL','Affected Employees']]
    for url in full_url_list:
        logger.info('scraper is on {}'.format(url))
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find('table') # output is list-type
    #     print(table)
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
    df['Suffix'] = df['URL'].str.strip('https://joblink.delaware.gov/ada')

    df = df.drop_duplicates(subset='URL', keep="first")
    all_de_data = pd.merge(de_data, df, left_on='url_suffix', right_on='Suffix')
    all_de_data.drop(columns=['Unnamed: 0','Suffix', 'url_suffix'], inplace=True)

    all_de_data.to_csv('{}/delaware_warn_raw.csv'.format(output_dir))


def get_total_results_count(soup):

    header_num = soup.find("td", class_="cfHeaderTitle")
    max_entries = header_num.text.split('of ')[1]
    max_entries = int(max_entries.split(')')[0])

    return max_entries


if __name__ == '__main__':
    scrape()