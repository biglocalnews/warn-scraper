import csv
import logging
import re
import requests

from bs4 import BeautifulSoup

from warn.cache import Cache
from warn.utils import write_rows_to_csv

logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/md.csv'
    # max_entries = 378 # manually inserted
    years = range(2019, 2009, -1)
    url = 'http://www.dllr.state.md.us/employment/warn.shtml'
    page = requests.get(url)
    logger.debug(f"Page status is {page.status_code} for {url}")
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all('table') # output is list-type
    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('td')
    output_header = []
    for header in headers:
        clean_txt = re.sub(r'\n', ' ', header.text)
        clean_txt = re.sub(r'\s+', ' ', clean_txt)
        output_header.append(clean_txt.strip())
    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    li_list = soup.find_all("a",{"class":"sub"})

    url = li_list[0]['href']
    url = f'http://www.dllr.state.md.us/employment/{url}'
    html = requests.get(url)
    logger.debug(f"Page status is {html.status_code} for {url}")
    write_body(html.text,output_csv)

    cache = Cache(cache_dir) # ~/.warn-scraper/cache
    scrape_old(li_list[1:],cache, output_csv)
    return output_csv

def write_body(html,output_csv):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all('table') # output is list-type
    output_rows = []
    for table_row in table[0].find_all('tr'):
        columns = table_row.find_all('td')
        output_row = []
        for column in columns:
            clean_txt = re.sub(r'\n', ' ', column.text)
            clean_txt = re.sub(r'\s+', ' ', clean_txt)
            output_row.append(clean_txt.strip())
        if output_row[0] != "Notice Date":
            output_rows.append(output_row)
    write_rows_to_csv(output_rows,output_csv,mode='a')

def scrape_page(url):
    response= requests.get(url)
    response.encoding = 'utf-8'
    return response.text

def scrape_old(url_list,cache, output_csv):
    for a in url_list:
        url = a['href']
        # Add the state postal as cache key prefix
        cache_key = f'md/{url}'
        try:
            html = cache.read(cache_key)
            logger.debug(f'Page fetched from cache: {cache_key}')
        except FileNotFoundError:
            # If file not found in cache, scrape the page and save to cache
            url = f'http://www.dllr.state.md.us/employment/{url}'
            html = scrape_page(url)
            cache.write(cache_key, html)
            logger.debug(f"Scraped and cached {url}")
        write_body(html,output_csv)