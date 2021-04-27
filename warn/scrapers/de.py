
import csv
import logging
import requests
import pandas as pd

from bs4 import BeautifulSoup

def scrape(output_dir):

    logger  = logging.getLogger(__name__)
    output_csv = '{}/delaware_warn_raw.csv'.format(output_dir)

    warn_links = get_warn_links()
    all_records = [['Company Name', 'Notice Date', 'Number of Employees Affected','City', 'ZIP', 'LWIB Area', 'WARN Type']]
    for link in warn_links:
        output_rows, list_info = scrape_warn_table(link, logger)
        list_of_records = scrape_record_link(list_info)

        full_records = combination(output_rows, list_of_records)
        all_records.extend(full_records)

    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(all_records)
    
    return

def get_warn_links():

    warn_links = ['https://joblink.delaware.gov/search/warn_lookups?commit=Search&page=1&q%5Bemployer_name_cont%5D=&q%5Bmain_contact_contact_info_addresses_full_location_city_matches%5D=&q%5Bnotice_eq%5D=&q%5Bnotice_on_gteq%5D=&q%5Bnotice_on_lteq%5D=&q%5Bservice_delivery_area_id_eq%5D=&q%5Bzipcode_code_start%5D=&utf8=%E2%9C%93']

    page = requests.get(warn_links[0])
    soup = BeautifulSoup(page.text, 'html.parser')
    pag_div = soup.find_all("div", class_="pagination")

    elem_a = pag_div[0].find_all('a')

    base = 'https://joblink.delaware.gov'
    for link in elem_a:
        label = link.get('aria-label')

        if label != None:
            link = link.get('href')
            full_link = base + link
            warn_links.append(full_link)

    return warn_links
    

def scrape_warn_table(link, logger):
        
    page = requests.get(link)
    logger.info("Page status code is {}".format(page.status_code))
    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.table
    output_rows = []
    for table_row in table.find_all('tr'):    
        columns = table_row.find_all('td')
        output_row = []

        for column in columns:
            output_row.append(column.text)
        output_row = [x.strip() for x in output_row]
        output_rows.append(output_row)

    list_info = []

    for a in table.find_all('a', href=True, text=True):
        link_text = [a['href']]

        if len(link_text[0]) <= 23:
            company_name = [a.text]
            company_name.extend(link_text)
            list_info.append(company_name)

    return output_rows, list_info

def scrape_record_link(list_info):
    
    base_url = 'https://joblink.delaware.gov/'
    
    all_records = []
    for record in list_info:
        record_link = record[1]
        full_link = base_url + record_link
        single_record = scrape_again(full_link)
        all_records.append(single_record)
        
    return all_records

def scrape_again(link):
    
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = soup.find("dl", class_="data")
    
    do_not_add = ['Company Name', 'Notice Date', 'Number of Employees Affected', 'Address', '', None]
    
    single_record = []
    for i in data:
        i = i.string
        if i != None:
            i = i.strip('\n')
        if i in do_not_add:
            continue
        single_record.append(i)
        
    return single_record

def combination(output_rows, list_of_records):
    output_rows = output_rows[1:]
    indexes = [0, 4]
    for row in output_rows:
        for index in sorted(indexes, reverse=True):
            del row[index]
            
    for row, record in zip(output_rows, list_of_records):
        record.extend(row)
        
    return list_of_records


if __name__ == '__main__':
    scrape()
       
