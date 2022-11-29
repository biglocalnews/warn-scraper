import logging
import re
import typing
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "chriszs"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Ohio Department of Job and Family Services",
    "url": "https://jfs.ohio.gov/warn/index.stm",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Ohio.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # Get the HTML
    base_url = "https://jfs.ohio.gov/warn/"
    r = utils.get_url(f"{base_url}index.stm")
    html = r.text

    # Save it to the cache
    state_code = "oh"
    cache.write(f"{state_code}/index.html", html)

    # Get the list of links
    soup = BeautifulSoup(html, "html5lib")
    link_list = soup.find(class_="warnYears").find_all("a")
    href_lookup = {a.text: a["href"] for a in link_list}

    # Loop through years and add any missing to the lookup
    most_recent_year = int(list(href_lookup.keys())[0])
    earliest_year = 2015  # We expect files to be available for at least 2015
    for year in range(earliest_year, most_recent_year):
        if str(year) not in href_lookup:
            href_lookup[str(year)] = f"{base_url}WARN{year}.stm"

    row_list = []

    # Loop through the links and scrape the data
    for year, href in href_lookup.items():
        # Form the URL
        if href.startswith("http"):
            url = href.replace("http://", "https://")
        else:
            url = f"{base_url}{href.replace('./', '')}"

        # If URL does not contain current or archive, assume it's a PDF
        if "archive" not in url and "current" not in url:
            cache_key = f"{state_code}/{year}.pdf"
        else:
            cache_key = f"{state_code}/{year}.html"

        # Get the file
        file_path = cache.download(cache_key, url)

        if str(file_path).endswith(".pdf"):
            # Parse the PDF
            row_list += _parse_pdf(file_path)
        else:
            # Parse the HTML
            row_list += _parse_html(file_path)

    header = list(filter(_is_header, row_list))[0]
    output_rows = [header] + list(filter(lambda row: not _is_header(row), row_list))

    # Write out
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the CSV
    return data_path


def _parse_html(file_path: Path) -> list:
    """
    Parse the table from the HTML.

    Keyword arguments:
    file_path -- the Path to the HTML file

    Returns: a list of lists of strings
    """
    # Get the HTML
    html = open(file_path).read()

    # Parse table
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all("table")

    # We expect the first table to be there with our data
    assert len(table_list) > 0
    table = table_list[1]

    # Parse the cells
    row_list = []
    for row in table.find_all("tr"):
        cell_list = row.find_all(["th", "td"])
        if not cell_list:
            continue
        cell_list = [c.text.strip() for c in cell_list]
        row_list.append(cell_list)

    # Return it
    return row_list


def _parse_pdf(pdf_path: Path) -> list:
    """
    Parse a PDF file and return a list of rows.

    Keyword arguments:
    pdf_path -- the Path to the PDF file

    Returns: a list of rows
    """
    # Loop through the PDF pages and scrape out the data
    row_list: list = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            rows = page.extract_table({"explicit_horizontal_lines": page.curves})
            assert rows
            for row_index, row in enumerate(rows):
                output_row = []
                for col_index, column in enumerate(row):
                    clean_text = _clean_text(column)

                    # If cell is empty, copy from the cell above it
                    # to deal with merged cells. Except for numbers, e.g. of employees,
                    # which we don't want to double count.
                    if (
                        clean_text == ""
                        and row_index > 0
                        and col_index < len(row_list[row_index - 1])
                        and row_list[row_index - 1][col_index] is not None
                        and not row_list[row_index - 1][col_index].strip().isnumeric()
                    ):
                        clean_text = row_list[row_index - 1][col_index]

                    output_row.append(clean_text)

                row_list.append(output_row)

    return row_list


def _clean_text(text: typing.Optional[str]) -> str:
    """
    Clean up text from a PDF cell.

    Keyword arguments:
    text -- the text to clean

    Returns: the cleaned text
    """
    if text is None:
        return ""
    # Collapse newlines
    partial = re.sub(r"\n", " ", text)
    # Standardize whitespace
    return re.sub(r"\s+", " ", partial)


def _is_header(row: list) -> bool:
    """
    Determine if a row is a header.

    Keyword arguments:
    row -- the row to check

    Returns: True if the row is a header, False otherwise
    """
    return (
        row[0].startswith("Date Rec")
        or row[0].startswith("DateReceived")
        or row[0].endswith("WARN Notices")
    )


if __name__ == "__main__":
    scrape()
