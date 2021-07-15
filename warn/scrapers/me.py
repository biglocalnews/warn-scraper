from warn.platforms.job_center.utils import scrape_state


def scrape(output_dir, cache_dir=None, use_cache=False):
    output_csv = f'{output_dir}/me.csv'
    search_url = 'https://joblink.maine.gov/search/warn_lookups'
    # Date chosen based on manual research
    stop_year = 2012
    # Use cache for years before current and prior year
    scrape_state(
        'ME',
        search_url,
        output_csv,
        stop_year,
        cache_dir,
        use_cache=use_cache
    )
    return output_csv
