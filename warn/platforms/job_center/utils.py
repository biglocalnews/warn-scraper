from datetime import datetime as dt

def scrape_dates(stop_year):
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
