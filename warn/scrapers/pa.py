import os
import re
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html"]


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Pennsylvania.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    state_code = "pa"
    cache = Cache(cache_dir)

    # The basic configuration for the scrape
    base_url = "https://www.dli.pa.gov"

    url = (
        f"{base_url}/Individuals/Workforce-Development/warn/notices/Pages/default.aspx"
    )
    response = utils.get_url(url)
    document = BeautifulSoup(response.text, "html.parser")
    links = document.find("table").find_all("a")

    output_rows = []

    for link in links:
        url = f"{base_url}/{link.get('href')}"
        cache_key = f"{state_code}/{os.path.basename(url).replace('.aspx', '')}.html"

        print(url)
        page = utils.get_url(url)
        html = page.text
        cache.write(cache_key, html)

        # Scrape out the table
        new_rows = _parse_table(html)

        # Concatenate the rows
        output_rows.extend(new_rows)

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the CSV
    return data_path


def _parse_table(html, include_headers=True):
    """
    Parse HTML table.

    Keyword arguments:
    html -- the HTML to parse
    include_headers -- whether to include the headers in the output (default True)

    Returns: a list of rows
    """
    # Parse out data table
    document = BeautifulSoup(html, "html.parser")
    records = document.find_all("table")[0].find_all("td")

    output_rows = []

    for record in records:
        company_name = record.find("strong")
        if company_name is not None:
            company_name = re.sub(r"\*[^\*]*\*", "", company_name.text).strip()
            print(company_name)
            output_rows.append([company_name])

    return output_rows


if __name__ == "__main__":
    scrape()
