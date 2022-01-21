import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache


def parse_table(html, id, include_headers=True):
    """
    Parse HTML table with given ID.

    Keyword arguments:
    html -- the HTML to parse
    id -- the ID of the table to parse
    include_headers -- whether to include the headers in the output (default True)

    Returns: a list of rows
    """

    # Parse out data table
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all(id=id)  # output is list-type

    # We expect the first table to be there with our data
    assert len(table_list) > 0
    table = table_list[0]

    output_rows = []
    column_tags = ["td"]

    if include_headers:
        column_tags.append("th")

    # Loop through the table and grab the data
    for table_row in table.find_all("tr"):
        columns = table_row.find_all(column_tags)
        output_row = []

        for column in columns:
            # Collapse newlines
            partial = re.sub(r"\n", " ", column.text)
            # Standardize whitespace
            clean_text = re.sub(r"\s+", " ", partial).strip()
            output_row.append(clean_text)

        # Skip any empty rows
        if len(output_row) == 0 or output_row == [""]:
            continue

        output_rows.append(output_row)

    return output_rows


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Georgia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """

    cache = Cache(cache_dir)

    state_code = "ga"
    base_url = "https://www.dol.state.ga.us/public/es/warn/searchwarns/list"
    data_path = f"{data_dir}/{state_code}.csv"

    area = 9  # statewide

    current_year = datetime.now().year
    first_year = 2002  # first available year

    years = list(range(first_year, current_year + 1))
    years.reverse()

    include_headers = True

    output_rows = []

    for year in years:
        url = f"{base_url}?geoArea={area}&year={year}&step=search"
        cache_key = f"{state_code}/{year}.html"

        # Read from cache if available and not this year or the year before
        if cache.exists(cache_key) and year < current_year - 1:
            html = cache.read(cache_key)
        else:
            page = utils.get_url(url)
            html = page.text
            cache.write(cache_key, html)

        new_rows = parse_table(html, "emplrList", include_headers=include_headers)

        output_rows = output_rows + new_rows

        include_headers = False

    utils.write_rows_to_csv(output_rows, data_path)

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
