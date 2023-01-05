import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["anikasikka"]
__tags__ = ["html"]
__source__ = {
    "name": "Colorado Department of Labor and Employment",
    "url": "https://cdle.colorado.gov/employers/layoff-separations/layoff-warn-list",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Colorado.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Grab the page
    page = utils.get_url(
        "https://cdle.colorado.gov/employers/layoff-separations/layoff-warn-list"
    )
    html = page.text

    # Write the raw file to the cache
    cache = Cache(cache_dir)
    cache.write("co/main/source.html", html)

    # Parse the page
    soup = BeautifulSoup(html, "html5lib")

    # Get the link to the Google Sheet that's on the page
    current_link = soup.find(class_="region-content").find("a", class_="btn-dark-blue")[
        "href"
    ]

    # Open the Google Sheet
    current_page = utils.get_url(current_link)
    current_html = current_page.text

    # Parse the Google Sheet
    soup_current = BeautifulSoup(current_html, "html5lib")
    table = soup_current.find(class_="waffle")
    cleaned_data = scrape_google_sheets(table)

    # Goes through the accordion links to get past data
    accordion_list = soup.find(class_="region-content").find_all("dl")

    # Make sure there's only one
    assert len(accordion_list) == 1

    # Grab the first one from the list
    accordion = accordion_list[0]

    link_list = [a for a in accordion.find_all("a") if "feedback" not in a.text]
    logger.debug(f"Requesting {len(link_list)} discovered links")
    for link in link_list:
        page = utils.get_url(link["href"])
        soup = BeautifulSoup(page.text, "html5lib")
        table = soup.find(class_="waffle")
        if "2017" in link.text:
            header_list = [
                "Company",
                "Layoff Total",
                "Workforce Region",
                "WARN Date",
                "Reason for Layoff",
            ]
        else:
            header_list = []
        cleaned_data += scrape_google_sheets(table, header_list)

    # Clean up the headers
    header_crosswalk = {
        "Company Name": "company",
        "Company": "company",
        "WARN Date": "notice_date",
        "Total Layoffs": "jobs",
        "NAICS": "naics",
        "Workforce Area": "workforce_area",
        "# Perm": "permanent_job_losses",
        "#Temp": "temporary_job_losses",
        "Reduced Hours": "reduced_hours",
        "#Furloughs": "furloughs",
        "Begin Date": "begin_date",
        "End Date": "end_date",
        "Reason for Layoffs": "reason",
        "Reason for Layoff": "reason",
        "WARN Letter": "letter",
        "Occupations Impacted": "occupations",
        "Occupations": "occupations",
        "Select the workforce area": "workforce_area",
        "Total number of permanent layoffs": "permanent_job_losses",
        "Total number of temporary layoffs": "temporary_job_losses",
        "Total number of furloughs": "furloughs",
        "Begin date of layoffs": "begin_date",
        "End date of layoffs": "end_date",
        "Layoff Total": "jobs",
        "Local Area": "workforce_area",
        "Layoff Date(s)": "begin_date",
        "Temp Layoffs": "temporary_job_losses",
        "Perm Layoffs": "permanent_job_losses",
        "Furloughs": "furloughs",
        "Workforce Local Area": "workforce_area",
        "Workforce Region": "workforce_region",
        "Contact Name": "contact",
        "Contact Phone": "phone",
        "Contact Email": "email",
        "FEIN": "fein",
        "Location Address": "location",
        "Total number of employees at the location": "at_the_location",
        "Sector 33 (6414) Guided Missle & Space Vehicle": "naics",
        "@dropdown": "dropdown",
    }
    standardized_data = []
    for row in cleaned_data:
        row_dict = {}
        for key, value in row.items():
            standardized_key = header_crosswalk[key]
            row_dict[standardized_key] = value
        standardized_data.append(row_dict)

    # Set the path to the final CSV
    output_csv = data_dir / "co.csv"

    # Write out the rows to the export directory
    # headers = list(cleaned_data[0].keys())
    utils.write_dict_rows_to_csv(
        output_csv, set(header_crosswalk.values()), standardized_data
    )

    # Return the path to the final CSV
    return output_csv


def scrape_google_sheets(table, header_list=None):
    """
    Scrapes data out of a Google Sheet.

    Keyword arguments:
    table -- A Google Sheet table pulled into BeautifulSoup
    header_list -- A list of header to use. Provide this when the source spreadsheet doesn't have a proper header row.

    Returns: The parsed data as a list of dictionaries
    """
    # If a header list isn't provided, pull one out automatically
    if not header_list:
        # Pull out the header row
        header_soup = table.find_all("tr")[1]

        # Parse the header row into a list,
        # preserving its order in the sheet
        header_list = []
        for cell in header_soup.find_all("td"):
            cell_text = cell.text.strip()
            # Skip empty headers
            if cell_text:
                header_list.append(cell_text)

    # Loop through all the data rows, which start
    # after the header and the little bar
    tr_list = table.find_all("tr")[3:]
    logger.debug(f"Parsing {len(tr_list)} rows")
    row_list = []
    for row in tr_list:
        # Only pull out the cells that have headers
        cell_list = row.find_all("td")[: len(header_list)]

        # Loop through the cells and key them into a dictionary using the header
        row_dict = {}
        for i, cell in enumerate(cell_list):
            row_dict[header_list[i]] = cell.text.strip()

        # Get values list for examination
        value_list = list(row_dict.values())

        # Skip empty rows
        if not any(value_list):
            continue

        # Skip header rows
        if "WARN Date" in value_list:
            continue

        # Keep whatever is left
        row_list.append(row_dict)

    # Return what we got
    return row_list


if __name__ == "__main__":
    scrape()
