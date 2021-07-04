import csv
import logging
from datetime import datetime as dt
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from warn.platforms import JobCenterSite
from warn.platforms.job_center.utils import scrape_dates
from warn.utils import write_dict_rows_to_csv


logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None, use_cache=True):
    output_csv = f'{output_dir}/ks.csv'
    search_url = 'https://www.kansasworks.com/search/warn_lookups'
    # Date chosen based on manual research
    stop_year = 1998
    yearly_dates = scrape_dates(stop_year)
    # No caching should be used for current and prior years,so
    # we have to separate those from remaining years.
    no_cache_years = [yearly_dates.pop(0), yearly_dates.pop(0)]
    # Set up scraper instance
    ks_cache_dir = str(Path(cache_dir,'ks'))
    site = JobCenterSite('KS', search_url, cache_dir=ks_cache_dir)
    # Execute the scraper in two batches
    # - Scrape current and prior year
    _scrape_years(site, output_csv, no_cache_years, use_cache=False)
    # - Scrape remaining years back to stop_year
    _scrape_years(site, output_csv, yearly_dates, use_cache=True)
    return output_csv

def _scrape_years(site, output_csv, start_end_dates, use_cache=True):
    current_year = dt.today().year
    # NOTE: Scraping for Jan 1 - Dec 31 for current year works
    # throughout the year. Additionally, it allows us to avoid
    # generating cache files for all days of the year.
    for start, end in start_end_dates:
        kwargs = {
            'start_date': start,
            'end_date': end,
            'use_cache': use_cache,
        }
        pages_dict, data = site.scrape(**kwargs)
        # Returned data includes search result page columns and
        # data from a nested dict, e.g. address and # of layoffs!
        headers = [k for k in data[0].keys() if k != 'detail']
        #TODO: extend headers with fields from nested 'detail' record dict
        rows = [_prepare_row(row) for row in data]
        # Use write mode on current year, append mode for all others
        write_mode = 'w' if start.startswith(str(current_year)) else 'a'
        write_dict_rows_to_csv(output_csv, headers, rows, mode=write_mode)

def _prepare_row(row):
    row.pop('detail')
    return row
