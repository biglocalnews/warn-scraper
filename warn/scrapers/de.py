from warn.platforms.job_center.utils import scrape_state


def scrape(output_dir, cache_dir=None, use_cache=True):
    output_csv = f"{output_dir}/de.csv"
    search_url = "https://joblink.delaware.gov/search/warn_lookups"
    # Date chosen based on manual research
    stop_year = 2007
    # Use cache for years before current and prior year
    scrape_state(
        "DE", search_url, output_csv, stop_year, cache_dir, use_cache=use_cache
    )
    return output_csv
