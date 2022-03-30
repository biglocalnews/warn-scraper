import re
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = [
    "html",
]
__source__ = {
    "name": "Alaska Department of Labor and Workforce Development",
    "url": "https://jobs.alaska.gov/RR/WARN_notices.htm",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Alaska.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get URL
    page = utils.get_url("https://jobs.alaska.gov/RR/WARN_notices.htm")

    # Force encoding to fix dashes, apostrophes, etc. on page.text from requests reponse
    page.encoding = "utf-8"

    # Parse out data table
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type

    # Loop through the table and grab the data
    output_rows = []
    for table_row in table[0].find_all("tr"):
        columns = table_row.find_all("td")
        output_row = []
        for column in columns:
            # Collapse newlines
            partial = re.sub(r"\n", " ", column.text)
            # Standardize whitespace
            clean_text = re.sub(r"\s+", " ", partial)
            output_row.append(clean_text)
        output_row = [x.strip() for x in output_row]
        if output_row == [""] or output_row[0] == "":
            continue
        output_rows.append(output_row)

    # Write out the data to a CSV
    data_path = data_dir / "ak.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the Path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
