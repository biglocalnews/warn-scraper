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
            for _i, page in enumerate(pdf.pages):

                # Pull out the table
                row_list = page.extract_table()

                # Skip empty pages
                if not row_list:
                    continue

                # Loop through each row in the table
                for row in row_list:

                    # Skip skinny and empty rows
                    values = [v for v in row if v]
                    if len(values) < 4:
                        continue

                    # Clean values
                    cell_list = [_clean_cell(c) for c in row]

                    # If the first cell is empty, pop it out
                    # This is a common bug in the PDFs
                    if not cell_list[0]:
                        cell_list.pop(0)

                    # Keep what's left
                    output_rows.append(cell_list)

    #                # Loop through the rows
    #                for row_index, row in enumerate(rows):
    #                    # Skip headers on all but first page of first PDF
    #                    if pdf_index > 0 and row_index == 0:
    #                        logger.debug(
    #                            f"Skipping header row on PDF {pdf_index+1} page {page_index+1}"
    #                        )
    #                        continue

    #    # Loop through the table and grab the data
    #    output_rows = []
    #    for table_row in table[0].find_all("tr"):
    #        columns = table_row.find_all("td")
    #        output_row = []
    #        for column in columns:
    #            # Collapse newlines
    #            partial = re.sub(r"\n", " ", column.text)
    #            # Standardize whitespace
    #            clean_text = re.sub(r"\s+", " ", partial)
    #            output_row.append(clean_text)
    #        output_row = [x.strip() for x in output_row]
    #        if output_row == [""] or output_row[0] == "":
    #            continue
    #        output_rows.append(output_row)

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
