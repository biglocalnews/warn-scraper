from datetime import datetime
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["palewire"]
__tags__ = [
    "html",
    "pdf",
]


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from South Carolina.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get URL
    r = utils.get_url(
        "https://scworks.org/employer/employer-programs/at-risk-of-closing/layoff-notification-reports",
        verify=False,
    )
    html = r.text

    # Save it to the cache
    cache = Cache(cache_dir)
    cache.write("sc/source.html", html)

    # Parse out the PDF links
    soup = BeautifulSoup(html, "html.parser")
    link_list = soup.find_all("a")
    pdf_list = [a for a in link_list if "pdf" in a["href"]]

    # Define crosswalks for how data is structured
    # by year and page
    schema = {
        2022: {
            1: {
                "company": 1,
                "location": 2,
                "date": 3,
                "jobs": 6,
                "type": 9,
                "naics": 10,
            }
        },
        2021: {
            1: {
                "company": 1,
                "location": 2,
                "date": 3,
                "jobs": 6,
                "type": 9,
                "naics": 10,
            },
            2: {
                "company": 1,
                "location": 2,
                "date": 3,
                "jobs": 4,
                "type": 5,
                "naics": 6,
            },
        },
        2020: {
            1: {
                "company": 1,
                "location": 2,
                "date": 7,
                "jobs": 6,
                "type": 4,
                "naics": 8,
            },
            2: {
                "company": 1,
                "location": 3,
                "date": 8,
                "jobs": 7,
                "type": 5,
                "naics": 9,
            },
        },
    }

    current_year = datetime.now().year
    output_rows = []
    for pdf in pdf_list:
        pdf_year = int(pdf.text[:4].strip())
        cache_key = f"sc/{pdf_year}.pdf"
        if cache.exists(cache_key) and pdf_year < (current_year - 1):
            pdf_path = cache.path / cache_key
        else:
            pdf_path = cache.download(
                cache_key, f"https://scworks.org/{pdf['href']}", verify=False
            )

        # Open the PDF
        with pdfplumber.open(pdf_path) as pdf:

            # Loop through the pages
            for i, page in enumerate(pdf.pages):

                # Pull out the table
                row_list = page.extract_table()

                # Skip empty pages
                if not row_list:
                    continue

                real_rows = []
                for row in row_list:
                    # Skip skinny and empty rows
                    values = [v for v in row if v]
                    if len(values) < 4:
                        continue
                    real_rows.append(row)

                # Loop through each row in the table
                for x, row in enumerate(real_rows):

                    # Skip the header on the first page
                    if i == 0 and x == 0:
                        continue

                    # Clean values
                    cell_list = [_clean_cell(c) for c in row]

                    # Pluck out the values in the old places we expect them
                    d = {}
                    print(cell_list)
                    for header, index in schema[pdf_year][i + 1].items():
                        d[header] = cell_list[index]
                    print(d)
                    # Keep what's left
                    output_rows.append(d)

    # Write out the data to a CSV
    data_path = data_dir / "sc.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the Path to the CSV
    return data_path


def _clean_cell(cell):
    """Clean the value in the provided cell."""
    if cell is None:
        return None
    return cell.strip().replace("\n", "")


if __name__ == "__main__":
    scrape()
