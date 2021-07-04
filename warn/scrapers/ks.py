import csv
import logging
from datetime import datetime as dt
from pathlib import Path

import pandas as pd
from warn.platforms.job_center.utils import scrape_state


def scrape(output_dir, cache_dir=None, use_cache=True):
    output_csv = f'{output_dir}/ks.csv'
    search_url = 'https://www.kansasworks.com/search/warn_lookups'
    # Date chosen based on manual research
    stop_year = 1998
    # Use cache for years before current and prior year
    scrape_state(
        'KS',
        search_url,
        output_csv,
        stop_year,
        cache_dir,
        use_cache=use_cache
    )
    return output_csv
