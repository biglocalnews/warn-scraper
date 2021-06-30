import csv
import itertools
import logging
import requests
import time

import pandas as pd
from bs4 import BeautifulSoup

from warn.cache import Cache
from warn.utils import write_rows_to_csv

logger  = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/newjersey_warn_raw.csv'
    url = 'http://lwd.state.nj.us/WorkForceDirectory/warn.jsp'
    logger.debug(f"Scraping {url}")
    html = scrape_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table') # output is list-type
    # The header and each line of company data lives in its own table.
    # Old school.
    header_table = tables.pop(0)
    headers = extract_fields_from_table(header_table)
    output_rows = [headers]
    # Process company "rows"
    for table in tables:
        layoff_data_row = extract_fields_from_table(table)
        output_rows.append(layoff_data_row)
    # Perform initial write of data
    write_rows_to_csv(output_rows, output_csv)
    cache = Cache(cache_dir) # ~/.warn-scraper/cache
    scrape_2010_to_2004(cache, output_csv)
    dedupe(output_csv)
    return output_csv

def scrape_page(url):
    response= requests.get(url)
    response.encoding = 'utf-8'
    return response.text

def extract_fields_from_table(table):
    row = table.find_all('tr')[0]
    data = []
    for field in row.find_all('td'):
        try:
            data.append(field.text.strip())
        except TypeError:
            import ipdb
            ipdb.set_trace()
    return data

def scrape_2010_to_2004(cache, output_csv):
    years = [2010, 2009, 2008, 2007, 2006, 2005, 2004]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year_month_pairs = itertools.product(years, months) # [(2010, 'Jan'), ...]
    for year, month in year_month_pairs:
        html_page_name = f'{month}{year}Warn.html'
        # Add the state postal as cache key prefix
        cache_key = f'nj/{html_page_name}'
        try:
            html = cache.read(cache_key)
            logger.debug(f'Page fetched from cache: {cache_key}')
        except FileNotFoundError:
            # If file not found in cache, scrape the page and save to cache
            url = f'https://www.nj.gov/labor/lwdhome/warn/{year}/{html_page_name}'
            html = scrape_page(url)
            cache.write(cache_key, html)
            logger.debug(f"Scraped and cached {url}")
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('table') # output is list-type
        output_rows = []
        for tr in table[0].find_all('tr'):
            row_data = [field.text.strip() for field in tr.find_all('td')]
            output_rows.append(row_data)
        # Remove header row
        output_rows.pop(0)
        if len(output_rows) > 0:
            write_rows_to_csv(output_rows, output_csv, mode='a')

def dedupe( output_csv):
    df = pd.read_csv(output_csv, keep_default_na = False)
    df.drop_duplicates(inplace = True, keep = 'first')
    df.to_csv(output_csv, index = False)
    return output_csv
