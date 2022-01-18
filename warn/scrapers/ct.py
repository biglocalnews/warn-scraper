import csv
import typing
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Connecticut.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "ct.csv"
    years = [2021, 2020, 2019, 2018, 2017, 2016, 2015]
    header_row = [
        "warn_date",
        "affected_company",
        "layoff_location",
        "number_workers",
        "layoff_date",
        "closing",
        "closing_date",
        "union",
        "union_address",
    ]
    output_rows = []
    for year in years:
        url = f"https://www.ctdol.state.ct.us/progsupt/bussrvce/warnreports/warn{year}.htm"
        response = utils.get_url(url)
        soup = BeautifulSoup(response.text, "html.parser")
        if year == 2016:
            table = soup.find_all("table", "style15")
        else:
            table = soup.find_all("table", "MsoNormalTable")
        table_rows = table[0].find_all("tr")
        # loop over table to process each row
        for table_row in table_rows:
            # skip 1st row because it is the header
            if table_rows.index(table_row) == 0:
                continue
            table_cells = table_row.find_all("td")
            # if a row has more than 9 cells it is handled separately
            # the 2016 table has some cells with nested tags
            if len(table_cells) > 9:
                output_row = _problem_cells(table_cells)
                output_rows.append(output_row)
            # if a row has less than 9 it is skipped because it is incomplete
            elif len(table_cells) < 9:
                continue
            else:
                # loop over cells for each row
                output_row = []
                for table_cell in table_cells:
                    cell = table_cell.text.strip()
                    cell = " ".join(cell.split())
                    output_row.append(cell)
                # test to see if the row is blank
                if not output_row:
                    continue
                output_rows.append(output_row)
        logger.debug(
            f"Scraping {len(output_rows)} total rows back through year {year}."
        )

    # save to csv
    with open(output_csv, "w") as out:
        writer = csv.writer(out)
        writer.writerow(header_row)
        writer.writerows(output_rows)
    return output_csv


# function to deal with problem rows in the 2016 table
def _problem_cells(table_cells):
    output_row = []
    for table_cell in table_cells:
        current_cell = table_cell.text.strip()
        current_cell = " ".join(current_cell.split())
        if table_cells.index(table_cell) == 0:
            output_row.append(current_cell)
        else:
            previous_index = table_cells.index(table_cell) - 1
            previous_cell = table_cells[previous_index].text.strip()
            previous_cell = " ".join(previous_cell.split())
            if current_cell == previous_cell:
                continue
            else:
                output_row.append(current_cell)
    return output_row


if __name__ == "__main__":
    scrape()
