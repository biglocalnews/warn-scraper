from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache


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
    # Grab the page
    page = utils.get_url(
        "https://www.tn.gov/workforce/general-resources/major-publications0/major-publications-redirect/reports.html"
    )
    html = page.text
    pdf_url = "https://www.tn.gov/content/dam/tn/workforce/documents/majorpublications/reports/WarnReportByMonth.pdf"
    pdf_file = download(pdf_url)

    # Write the raw file to the cache
    cache = Cache(cache_dir)
    cache.write("tn/source.html", html)
    cache.write("tn/pdffile.pdf", pdf_file)

    # Parse the source file and convert to a list of rows, with a header in the first row.
    # It's up to you to fill in the blank here based on the structure of the source file.
    # You could do that here with BeautifulSoup or whatever other technique.
    soup = BeautifulSoup(html, "html.parser")
    data_list = soup.find_all("p")

    # getting headers from pdf
    tn_headers = [
        "Notice Date",
        "Effective Date",
        "Received Date",
        "Company",
        "City",
        "County",
        "No. Of Employees",
        "Layoff/Closure",
    ]
    cleaned_data = [tn_headers]

    i = 0
    for data in data_list:
        if i != 0:
            # splitting the data on its delimiter
            items = str(data).split("|")
            raw_data = []
            # making sure that the last item in the list is the data value of interest; splitting based on last character of each text-html data sequence
            for item in items:
                components = (
                    item.replace("</a>", "")
                    .replace("</p>", "")
                    .replace("<strong>", "")
                    .replace("<br/>", "")
                    .split(">")
                )
                raw_data.append(components[-1])
            nice_data = []
            # discarding bad data — only extracting data that has all the relevant information
            if len(raw_data) == 6:
                nice_data.append(raw_data[0])
                nice_data.append(raw_data[4])
                nice_data.append("")
                nice_data.append(raw_data[1])
                nice_data.append("")
                nice_data.append(raw_data[2])
                nice_data.append(raw_data[3])
                nice_data.append(raw_data[5])
                cleaned_data.append(nice_data)
        i += 1

    with pdfplumber.open(pdf_file) as pdf:
        i = 0
        for my_page in pdf.pages:
            # all even pages have data, odd pages don't have the data
            if i % 2 == 0:
                all_extracted_tables = my_page.extract_tables()
                for table in all_extracted_tables:
                    for rows in table:
                        # to remove redundant headers
                        if (
                            rows[0] == "Notice Date"
                            or rows[0] == ""
                            or rows[0] == "Summary by Month"
                        ):
                            continue
                        cleaned_data.append(rows)
            i += 1

    # Set the path to the final CSV
    # We should always use the lower-case state postal code, like nj.csv
    output_csv = data_dir / "tn.csv"

    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, cleaned_data)

    # Return the path to the final CSV
    return output_csv


def download(url):
    """Download the pdf url."""
    file = url.split("/")[-1]
    with requests.get(url) as r:
        with open(file, "wb") as f:
            f.write(r.content)

    return file


if __name__ == "__main__":
    scrape()
