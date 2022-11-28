import typing
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["anikasikka"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Tennessee Department of Labor and Workforce Development",
    "url": "https://www.tn.gov/workforce/general-resources/major-publications0/major-publications-redirect/reports.html",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Tennessee.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Initialize the cache
    cache = Cache(cache_dir)

    # Grab the HTML page with the latest years of data
    page = utils.get_url(
        "https://www.tn.gov/workforce/general-resources/major-publications0/major-publications-redirect/reports.html"
    )
    html = page.text
    cache.write("tn/source.html", html)

    # Grab the PDF with the archived historial data
    pdf_url = "https://www.tn.gov/content/dam/tn/workforce/documents/majorpublications/reports/WarnReportByMonth.pdf"
    pdf_file = cache.download("tn/pdffile.pdf", pdf_url)

    # Set the headers we'll use for both sources
    tn_headers = [
        "Notice Date",
        "Effective Date",
        "Received Date",
        "Company",
        "City",
        "County",
        "No. Of Employees",
        "Layoff/Closure",
        "Notice ID",
    ]
    cleaned_data: typing.List[typing.Any] = [tn_headers]

    # Parse the latest HTML file and convert to a list of rows, with a header in the first row.
    soup = BeautifulSoup(html, "html5lib")

    # Grab all the list items on the page
    data_list = soup.find_all("p")

    # Loop through them all, skipping the first item, which is a header
    for data in data_list[1:]:

        # splitting the data on its delimiter
        items = str(data).split("|")

        # making sure that the last item in the list is the data value of interest
        # splitting based on last character of each text-html data sequence
        raw_data = []
        for item in items:
            value_html = item.split(":")[-1]
            value_soup = BeautifulSoup(value_html, "html5lib")
            string_list = list(value_soup.stripped_strings)
            value = string_list[-1]
            raw_data.append(value)

        # If there aren't six entries it's junk
        if len(raw_data) != 6:
            continue

        # Pluck out the values we want
        nice_data = [
            raw_data[0],  # Notice Date
            raw_data[4],  # Effective Date
            "",  # Received Date
            raw_data[1],  # Company
            "",  # City
            raw_data[2],  # County
            raw_data[3],  # Number of employees
            "",  # Layoff/Closure
            raw_data[5],  # Notice ID
        ]

        # Add them to the master list
        cleaned_data.append(nice_data)

    # The PDF header blacklist of rows to toss
    pdf_header_blacklist = [
        "Notice Date",
        "Total",
    ]

    # Open the PDF
    with pdfplumber.open(pdf_file) as pdf:

        # Loop through all the pages
        for i, my_page in enumerate(pdf.pages):

            # Sll even pages have data, odd pages don't have the data
            if i % 2 != 0:
                continue

            # Pull out the table and loop through the rows
            table = my_page.extract_table()
            if not table:
                continue

            # Cut empty rows
            row_list = [r for r in table if any(r)]
            if not row_list:
                continue

            # If this is a summary table, skip it
            first_cell = row_list[0][0]
            assert first_cell
            if first_cell.lower().strip() == "summary by month":
                continue

            # Loop through all the rows ...
            for row in row_list:

                # Skip remove redundant headers
                if row[0] in pdf_header_blacklist:
                    continue

                # Toss in an empty Notice ID since it isn't in the PDF
                row.append("")

                # Add the data to our output
                cleaned_data.append(row)

    # Set the path to the final CSV
    output_csv = data_dir / "tn.csv"

    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, cleaned_data)

    # Return the path to the final CSV
    return output_csv


if __name__ == "__main__":
    scrape()
