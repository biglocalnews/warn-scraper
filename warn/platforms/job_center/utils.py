from datetime import datetime as dt
from pathlib import Path

from .site import Site as  JobCenterSite
from warn.utils import write_dict_rows_to_csv



def scrape_state(state_postal, search_url, output_csv, stop_year, cache_dir, use_cache=True):
    """Date-based scraper for Job Center states

    This is the primary interface that should be used by downstream scrapers.
    It applies a date-based scraping strategy that:

      - Scrapes one year at a time, in reverse chronological order
      - Always does a fresh scrape for current and prior year
      - Uses cached files for years before current & prior

    Args:

        state_postal (str): Two-letter all-caps state postal (e.g. KS)
        search_url (str): Base search url (e.g. https://www.kansasworks.com/search/warn_lookups)
        output_csv (str): Full path to CSV where data should be saved (e.g. ~/.warn-scraper/exports/ks.csv)
        stop_year (int): First year that data is available for state (requires manaul research)
        cache_dir (str): The root directory for WARN's cache files (e.g. ~/.warn-scraper/cache)
        use_cache (boolean, default True): Whether to use cached files for older years

    Returns:

        Full path to exported csv (e.g. ~/.warn-scraper/exports/ks.csv)

    """
    yearly_dates = _date_ranges_to_scrape(stop_year)
    # No caching should be used for current and prior year, so
    # we have to separate those from remaining years.
    no_cache_years = [yearly_dates.pop(0), yearly_dates.pop(0)]
    # Set up scraper instance
    state_cache_dir = str(Path(cache_dir, state_postal.lower()))
    site = JobCenterSite(state_postal.upper(), search_url, cache_dir=state_cache_dir)
    # Execute the scrape in two batches
    # 1. Current and prior year. Always scrape fresh (i.e. never use cached files)
    #    in case records have been updated.
    _scrape_years(site, output_csv, no_cache_years, use_cache=False)
    # 2. Years before current & prior, going back to stop_year.
    #    We should generally use cached files for these older years,
    #    since data is less likely to be updated.
    _scrape_years(site, output_csv, yearly_dates, use_cache=use_cache)
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

def _date_ranges_to_scrape(stop_year):
    """Generates a list of start/end pairs from
    current year to some year in the past
    """
    start = '{}-01-01'
    end = '{}-12-31'
    current_year = dt.today().year
    years = sorted(range(stop_year, current_year +1), reverse=True)
    yearly_dates = []
    for year in years:
        yearly_dates.append(
            (start.format(year), end.format(year))
        )
    return yearly_dates
