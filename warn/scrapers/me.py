from warn.platforms.job_center.utils import scrape_state


def scrape(output_dir, cache_dir=None, use_cache=False):
    """
    Scrape data from Maine.

    Arguments:
    output_dir -- the Path were the result will be saved

    Keyword arguments:
    cache_dir -- the Path where results can be cached (default None)
    use_cache -- a Boolean indicating whether the cache should be used (default True)

    Returns: the Path where the file is written
    """
    output_csv = f"{output_dir}/me.csv"
    search_url = "https://joblink.maine.gov/search/warn_lookups"
    # Date chosen based on manual research
    stop_year = 2012
    # Use cache for years before current and prior year
    scrape_state(
        "ME", search_url, output_csv, stop_year, cache_dir, use_cache=use_cache
    )
    return output_csv
