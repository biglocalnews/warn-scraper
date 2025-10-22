import csv
import logging
import typing
from pathlib import Path

import requests
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache

__authors__ = [
    "palewire",
    "stucka",
]
__tags__ = [
    "excel",
]
__source__ = {
    "name": "Kentucky Career Center",
    "url": "https://kcc.ky.gov/employer/Pages/Business-Downsizing-Assistance---WARN.aspx",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Kentucky.

    Arguments:
    output_dir -- the Path were the result will be saved

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get the latest workbook
    cache = Cache(cache_dir)
    hostpage = "https://kcc.ky.gov/Pages/News.aspx"
    baseurl = "https://kcc.ky.gov"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0"
    }
    r = requests.get(hostpage, headers=headers)
    html = r.text
    subpage = html.split("WARN Notices by Year</h4")[-1]
    # mypy and BeautifulSoup are not cooperating. So ... extract the URL in a dumb way.
    fragment = subpage.split('href="')[1].split('"')[0]
    latest_url = f"{baseurl}{fragment}"

    # latest_url = "https://kcc.ky.gov/WARN%20notices/WARN%20NOTICES%202022/WARN%20Notice%20Report%2001262022.xls"
    latest_path = cache.download("ky/latest.xlsx", latest_url)

    # Open it up
    workbook = load_workbook(filename=latest_path)

    crosswalk = {
        "Closure or Layoff?": "closure_or_layoff",
        "Company Name": "company",
        "Company: Company Name": "company",
        "County": "county",
        "Date Received": "date_received",
        "Employees": "employees",
        "NAICS": "NAICS",
        "NAICS Code": "NAICS",
        "Notice Link": "notice_url",
        "Notice Type": "source",
        "Notice URL": "notice_url",
        "Notice: Notice Number": "notice_number",
        "Number of Employees Affected": "employees",
        "Projected Date": "date_effective",
        "Region": "region",
        "Trade": "trade",
        "Type of Employees Affected": "union_affected",
        "Workforce Board": "region",
        "address": "address",
        "comments": "comments",
        "congressional": "congressional",
        "contact": "contact",
        "industry": "industry",
        "neg": "neg",  # Rarely seen, only in historical data, maybe all with "N"
        "occupations": "industry",
        "source": "source",
        "union": "union",  # Unclear if different than types of employees affected/union_affected
    }

    masterlist: list = []
    for sheet in workbook.worksheets:
        localrows = parse_xlsx(sheet)

        # Traverse each tab. Assume the first line is a header. Check if the second line is bogus.
        # Build a list of dicts.
        # Assuming the first line is a header began failing in 10/2025.

        # logger.debug(localrows)

        headerrowindex = None
        afterlastrowindex = None
        for rowindex, localrow in enumerate(localrows):
            rowstandin = ""
            for item in localrow:
                rowstandin += str(item)
            if "Company Name" in rowstandin:
                headerrowindex = rowindex
            if "Total" in rowstandin and "Count" in rowstandin:
                afterlastrowindex = rowindex
        if not headerrowindex:
            logger.error("Unable to find header row.")
        if not afterlastrowindex:
            logger.warning("Unable to find last row")
            afterlastrowindex = len(localrows)
        localheadersraw: list = localrows[headerrowindex]  # type: ignore

        nullcount = 0

        localheaders: list = []
        for entry in localheadersraw:
            if entry not in crosswalk:
                if entry is None:
                    nullcount += 1
                    localheaders.append(f"null_{nullcount}")
                else:
                    logger.error(f"Potential header {entry} not found in crosswalk.")
            else:  # We actually have a good header!
                localheaders.append(crosswalk[entry])

        for row in localrows[
            headerrowindex + 1 : afterlastrowindex  # type: ignore
        ]:  # Skip the header row
            if row[0] != "Date Received":  # Check for fake second header
                line: dict = {}
                for i, fieldname in enumerate(localheaders):
                    line[fieldname] = row[i]
                    if isinstance(row[i], str):
                        line[fieldname] = row[i].strip()
                masterlist.append(line)

    logger.debug(f"Successfully merged {len(masterlist)} records from new spreadsheet.")

    # Earlier versions of this code needed the archived data to match the new data.
    # We can no longer expect that since October 2025 data revisions.

    archive_url = "https://storage.googleapis.com/bln-data-public/warn-layoffs/ky-historical-normalized.csv"

    logger.debug("Getting KY historical data")
    r = requests.get(archive_url)

    reader = list(csv.reader(r.text.splitlines()))

    localheadersraw = reader[0]
    localheaders: list = []  # type: ignore
    for entry in localheadersraw:
        if entry not in crosswalk:
            logger.error(f"Cannot match possible header value of {entry} to crosswalk.")
        else:
            localheaders.append(crosswalk[entry])
    for row in reader[1:]:  # Skip header row
        line: dict = {}  # type: ignore
        for i, fieldname in enumerate(localheaders):
            line[fieldname] = row[i]
            if isinstance(row[i], str):
                line[fieldname] = row[i].strip()
        masterlist.append(line)
    logger.debug("Historical records folded in.")

    # Write out the results
    data_path = data_dir / "ky.csv"
    utils.write_disparate_dict_rows_to_csv(data_path, masterlist)

    # Pass it out
    return data_path


def parse_xlsx(worksheet) -> typing.List[typing.List]:
    """Parse the Excel xlsx file at the provided path.

    Args:
        worksheet: An openpyxl worksheet ready to parse

    Returns: List of values ready to write.
    """
    # Convert the sheet to a list of lists
    row_list = []
    for r in worksheet.rows:
        # Parse cells
        cell_list = [cell.value for cell in r]

        # Skip empty rows
        try:
            # A list with only empty cells will throw an error
            next(c for c in cell_list if c)
        except StopIteration:
            continue

        # Add to the master list
        row_list.append(cell_list)

    # Pass it back
    return row_list


if __name__ == "__main__":
    scrape()
