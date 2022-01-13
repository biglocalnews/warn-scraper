from warn.platforms.job_center.utils import scrape_state


def scrape(output_dir, cache_dir=None, use_cache=True):
    output_csv = f"{output_dir}/vt.csv"
    search_url = "https://www.vermontjoblink.com/search/warn_lookups"
    # Date chosen based on manual research
    stop_year = 2003
    # Use cache for years before current and prior year
    scrape_state(
        "VT", search_url, output_csv, stop_year, cache_dir, use_cache=use_cache
    )
    return output_csv
