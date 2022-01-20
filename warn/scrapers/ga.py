import re
import typing
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Georgia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    area = 9  # statewide

    current_year = datetime.now().year
    first_year = 2002  # first available year

    years = list(range(first_year, current_year))
    years.reverse()

    # include column headers in first row
    column_tags = ["td", "th"]

    output_rows = []

    for year in years:
        url = f"https://www.dol.state.ga.us/public/es/warn/searchwarns/list?geoArea={area}&year={year}&step=search"

        # Get URL
        page = utils.get_url(url)

        # Force encoding to fix dashes, apostrophes, etc. on page.text from requests reponse
        page.encoding = "utf-8"

        # Parse out data table
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.find_all(id="emplrList")  # output is list-type

        # Loop through the table and grab the data
        for table_row in table[0].find_all("tr"):
            columns = table_row.find_all(column_tags)
            output_row = []

            for column in columns:
                # Collapse newlines
                partial = re.sub(r"\n", " ", column.text)
                # Standardize whitespace
                clean_text = re.sub(r"\s+", " ", partial)
                output_row.append(clean_text)

            output_row = [x.strip() for x in output_row]

            if len(output_row) == 0 or output_row == [""]:
                continue

            output_rows.append(output_row)

        # exclude column headers on subsequent years
        column_tags = ["td"]

    # Write out the data to a CSV
    data_path = data_dir / "ga.csv"
    utils.write_rows_to_csv(output_rows, data_path)

    # Return the Path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
