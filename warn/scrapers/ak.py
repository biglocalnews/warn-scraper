import re
import requests

from bs4 import BeautifulSoup

from warn.utils import write_rows_to_csv


def scrape(output_dir, cache_dir=None):
    """
    Scrape data from Alaska.

    Arguments:
    output_dir -- the Path were the result will be saved

    Keyword arguments:
    cache_dir -- the Path where results can be cached (default None)

    Returns: the Path where the file is written
    """
    output_csv = f"{output_dir}/ak.csv"
    url = "https://jobs.alaska.gov/RR/WARN_notices.htm"
    page = requests.get(url)
    # Force encoding to fix dashes, apostrophes, etc. on page.text from requests reponse
    page.encoding = "utf-8"
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")  # output is list-type
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
    write_rows_to_csv(output_rows, output_csv)
    return output_csv
