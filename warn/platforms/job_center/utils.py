import logging
import re
from collections import OrderedDict
from datetime import datetime as dt

from ... import utils
from .site import Site as JobCenterSite

logger = logging.getLogger(__name__)


def scrape_state(
    state_postal, search_url, output_csv, stop_year, cache_dir, use_cache=True
):
    """Date-based scraper for Job Center states.

    This is the primary interface that should be used by downstream scrapers.
    It applies a date-based scraping strategy that:

      - Scrapes one year at a time, in reverse chronological order
      - Always does a fresh scrape for current and prior year
      - Uses cached files for years before current & prior
      - Deduplicates search results

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
    state_cache_dir = cache_dir / state_postal.lower()
    site = JobCenterSite(state_postal.upper(), search_url, cache_dir=state_cache_dir)

    # Date-based searches produce search result pages that appear to have certain
    # records duplicated over paged results. We'll initially write all data to a raw
    # file which we then deduplicate to produce the final output_csv.
    raw_csv = cache_dir / f"{state_postal.lower()}_raw.csv"
    logger.debug(f"Generating {raw_csv}")

    # 0. Write header row first
    headers = [
        "employer",
        "notice_date",
        "number_of_employees_affected",
        "warn_type",
        "city",
        "zip",
        "lwib_area",
        "address",
        "record_number",
        "detail_page_url",
    ]
    utils.write_rows_to_csv(raw_csv, [headers])
    # Execute the scrape in two batches
    # 1. Current and prior year. Always scrape fresh (i.e. never use cached files)
    #    in case records have been updated.
    _scrape_years(site, raw_csv, headers, no_cache_years, use_cache=False)
    # 2. Years before current & prior, going back to stop_year.
    #    We should generally use cached files for these older years,
    #    since data is less likely to be updated.
    _scrape_years(site, raw_csv, headers, yearly_dates, use_cache=use_cache)
    _dedupe(raw_csv, output_csv)
    return output_csv


def _scrape_years(site, output_csv, headers, start_end_dates, use_cache=True):
    """Loop through years of data and write out to CSV."""
    # NOTE: Scraping for Jan 1 - Dec 31 for current year works
    # throughout the year. Additionally, it allows us to avoid
    # generating cache files for all days of the year.
    for start, end in start_end_dates:
        kwargs = {
            "start_date": start,
            "end_date": end,
            "use_cache": use_cache,
        }
        pages_dict, data = site.scrape(**kwargs)
        rows = [_prepare_row(row) for row in data]
        # We previously wrote the header so use append mode for data rows
        utils.write_dict_rows_to_csv(output_csv, headers, rows, mode="a")


def _prepare_row(row):
    """Flatten the nested dict for downstream export to CSV."""
    # Returned data includes fields from search result page and
    # data from detail page record for each layoff notice
    # the latter contains two key fields (address and number affected)
    detail = row.pop("detail")
    row["number_of_employees_affected"] = detail["number_of_employees_affected"]
    row["address"] = re.sub(r"\n+", "; ", detail["address"].strip())
    row["record_number"] = detail["record_number"]
    return row


def _date_ranges_to_scrape(stop_year):
    """Generate a list of start/end pairs from current year to some year in the past."""
    start = "{}-01-01"
    end = "{}-12-31"
    current_year = dt.today().year
    years = sorted(range(stop_year, current_year + 1), reverse=True)
    yearly_dates = []
    for year in years:
        yearly_dates.append((start.format(year), end.format(year)))
    return yearly_dates


def _dedupe(raw_csv, output_csv):
    """Create an ordered dict to discard dupes while preserving row order."""
    data = OrderedDict()
    raw_count = 0
    utils.create_directory(raw_csv, is_file=True)
    with open(raw_csv, newline="") as src:
        for row in src:
            raw_count += 1
            data[row] = row
    # Write the deduped rows to final output_csv
    final_count = 0
    utils.create_directory(output_csv, is_file=True)
    with open(output_csv, "w", newline="") as out:
        for row in data.keys():
            final_count += 1
            out.write(row)
    num_removed = raw_count - final_count
    if num_removed > 0:
        logger.debug(f"Removed {num_removed} duplicate records from {raw_csv}")
    return output_csv
