import logging
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from .. import utils
from ..cache import Cache

__authors__ = ["anikasikka", "stucka"]
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
    content_region = soup.find(class_="region-content")
    if isinstance(content_region, Tag):
        current_link = content_region.find("a", class_="btn-dark-blue")
    else:
        raise ValueError("Could not find content region")
    if isinstance(current_link, Tag):
        current_href = current_link["href"]
    else:
        raise ValueError("Could not find Google Sheet link")

    # Scraper had been working off partially loaded impression of the HTML in the dOM.
    # This keyboard is not helping.
    # Anyway, instead of trying to get a partially complete version and parse the HTML there,
    # let's try to get the actual HTML export of the page.
    # 2016 has a different filename schema we need to account for.

    if "/edit" in current_href:
        better_link = current_href.split("/edit")[0] + "/gviz/tq?tqx=out:html"  # type: ignore
    elif "drive.google.com/open?id=" in current_href:  # Work from the ID
        better_link = "https://docs.google.com/spreadsheets/d/"
        better_link += current_href.split("open?id=")[-1]  # type: ignore
        better_link += "/gviz/tq?tqx=out:html"
    else:
        raise ValueError(f"Could not adapt {current_href} to find HTML export.")

    # Open the Google Sheet
    current_page = utils.get_url(better_link)
    current_html = current_page.text

    # Parse the Google Sheet
    soup_current = BeautifulSoup(current_html, "html5lib")
    # table = soup_current.find(class_="waffle")
    table = soup_current.find("table")
    cleaned_data = scrape_google_sheets(table)

    # Goes through the accordion links to get past data
    content_region = soup.find(class_="region-content")
    if isinstance(content_region, Tag):
        accordion_list = content_region.find_all("dl")
    else:
        raise ValueError("Could not find content region")

    # Make sure there's only one
    assert len(accordion_list) == 1

    # Grab the first one from the list
    accordion = accordion_list[0]

    link_list = [a for a in accordion.find_all("a") if "feedback" not in a.text]
    logger.debug(f"Requesting {len(link_list)} discovered links")
    for link in link_list:
        bad_url = link["href"]
        # Scraper had been working off partially loaded impression of the HTML in the dOM.
        # This keyboard is not helping.
        # Anyway, instead of trying to get a partially complete version and parse the HTML there,
        # let's try to get the actual HTML export of the page.
        # 2016 has a different filename schema we need to account for.

        if "/edit" in bad_url:
            better_link = bad_url.split("/edit")[0] + "/gviz/tq?tqx=out:html"
        elif "drive.google.com/open?id=" in bad_url:
            better_link = "https://docs.google.com/spreadsheets/d/"
            better_link += bad_url.split("open?id=")[-1]  # Get just the Id
            better_link += "/gviz/tq?tqx=out:html"
        else:
            raise ValueError(f"Could not adapt {bad_url} to find HTML export.")

        page = utils.get_url(better_link)

        soup = BeautifulSoup(page.text, "html5lib")
        table = soup.find("table")
        if "2017" in link.text:
            header_list = [
                "Company",
                "Layoff Total",
                "Workforce Region",
                "WARN Date",
                "Reason for Layoff",
            ]
        elif "2019" in link.text:
            header_list = [
                "Company Name",
                "Layoff Total",
                "Workforce Local Area",
                "WARN Date",
                "Reason for Layoff",
                "Occupations",
                "Layoff Date(s)",
            ]
        else:
            header_list = []
        cleaned_data += scrape_google_sheets(table, header_list)

    # Clean up the headers
    header_crosswalk = {
        "Company Name": "company",
        "Company": "company",
        "Name": "company",
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
        "Total CO": "jobs",
        "CO Layoffs": "jobs",
        "Total number of permanent layoffs": "permanent_job_losses",
        "# permanent": "permanent_job_losses",
        "# Permanent": "permanent_job_losses",
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
        "Received": "received_date",
        "Notes": "notes",
        # Only add new matches above here, not below here.
    }

    header_garbage = {
        # And then it got ugly with some columns getting unhidden.
        "Timestamp": "timestamp",
        "Email Address": "email_address",
        "Is this a NEW WARN or a REVISION?": "is_this_a_new_warn_or_a_revision",
        "Total number of employees with reduced hours": "total_number_of_employees_with_reduced_hours",
        "Include the total number of employees on or expected to be on a Workshare plan.": "include_the_total_number_of_employees_on_or_expected_to_be_on_a_workshare_plan",
        "Expected date of second job losses at location 1": "expected_date_of_second_job_losses_at_location_1",
        "Expected end date of second job losses at location 1": "expected_end_date_of_second_job_losses_at_location_1",
        "Expected date of third job losses at location 1": "expected_date_of_third_job_losses_at_location_1",
        "Expected end date of third job losses at location 1": "expected_end_date_of_third_job_losses_at_location_1",
        "Do the employees have bumping rights?": "do_the_employees_have_bumping_rights",
        "Are the employees represented by a union?": "are_the_employees_represented_by_a_union",
        "If you selected Rural Consortium for the workforce area, please choose a subarea using the map.": "if_you_selected_rural_consortium_for_the_workforce_area_please_choose_a_subarea_using_the_map",
        "Name of union(s)": "name_of_unions",
        "Contact phone number for union representative(s)": "contact_phone_number_for_union_representatives",
        "Email address for union representative(s)": "email_address_for_union_representatives",
        "Address, City, ZIP for Union 1": "address_city_zip_for_union_1",
        "Has a second location been impacted?": "has_a_second_location_been_impacted",
        "Location 2 Address": "location_2_address",
        "Total number of employees at location 2": "total_number_of_employees_at_location_2",
        "Total number of permanent layoffs at location 2": "total_number_of_permanent_layoffs_at_location_2",
        "Total number of temporary layoffs at location 2": "total_number_of_temporary_layoffs_at_location_2",
        "Total number of furloughs at location 2": "total_number_of_furloughs_at_location_2",
        "Total number of employees with reduced hours at location 2": "total_number_of_employees_with_reduced_hours_at_location_2",
        "Total number of employees on workshare plan at location 2": "total_number_of_employees_on_workshare_plan_at_location_2",
        "Occupations Impacted at location 2": "occupations_impacted_at_location_2",
        "Expected date of first job losses at location 2": "expected_date_of_first_job_losses_at_location_2",
        "Contact name(s) for union representative(s)": "contact_names_for_union_representatives",
        "Expected end date of first job losses at location 2": "expected_end_date_of_first_job_losses_at_location_2",
        "Expected date of second job losses at location 2": "expected_date_of_second_job_losses_at_location_2",
        "Expected end date of second job losses at location 2": "expected_end_date_of_second_job_losses_at_location_2",
        "Expected date of third job losses at location 2": "expected_date_of_third_job_losses_at_location_2",
        "Expected end date of third job losses at location 2": "expected_end_date_of_third_job_losses_at_location_2",
        "Reason for Layoffs at location 2": "reason_for_layoffs_at_location_2",
        "Do employees at location 2 having bumping rights?": "do_employees_at_location_2_having_bumping_rights",
        "Are employees at location 2 represented by a union?": "are_employees_at_location_2_represented_by_a_union",
        "Select the workforce area for location 2": "select_the_workforce_area_for_location_2",
        "If you selected Other/Sub-Area, please choose a location from the following dropdown menu:": "if_you_selected_othersub_area_please_choose_a_location_from_the_following_dropdown_menu",
        "Name of Union 2": "name_of_union_2",
        "Contact name for Union 2": "contact_name_for_union_2",
        "Contact phone number for Union 2": "contact_phone_number_for_union_2",
        "Email address for Union 2": "email_address_for_union_2",
        "Address, City, ZIP for Union 2": "address_city_zip_for_union_2",
        "Has a third location been impacted?": "has_a_third_location_been_impacted",
        "Location 3 Address": "location_3_address",
        "Total number of employees at location 3": "total_number_of_employees_at_location_3",
        "Total number of permanent layoffs at location 3": "total_number_of_permanent_layoffs_at_location_3",
        "Total number of temporary layoffs at location 3": "total_number_of_temporary_layoffs_at_location_3",
        "Total number of furloughs at location 3": "total_number_of_furloughs_at_location_3",
        "Total number of employees with reduced hours at location 3": "total_number_of_employees_with_reduced_hours_at_location_3",
        "Total number of employees on workshare plan at location 3": "total_number_of_employees_on_workshare_plan_at_location_3",
        "Occupations Impacted at location 3": "occupations_impacted_at_location_3",
        "Expected date of first job losses at location 3": "expected_date_of_first_job_losses_at_location_3",
        "Expected end date of first job losses at location 3": "expected_end_date_of_first_job_losses_at_location_3",
        "Expected date of second job losses at location 3": "expected_date_of_second_job_losses_at_location_3",
        "Expected end date of second job losses at location 3": "expected_end_date_of_second_job_losses_at_location_3",
        "Expected date of third job losses at location 3": "expected_date_of_third_job_losses_at_location_3",
        "Expected end date of third job losses at location 3": "expected_end_date_of_third_job_losses_at_location_3",
        "Reason for Layoffs at location 3": "reason_for_layoffs_at_location_3",
        "Do employees at location 3 having bumping rights?": "do_employees_at_location_3_having_bumping_rights",
        "Are employees at location 3 represented by a union?": "are_employees_at_location_3_represented_by_a_union",
        "Select the workforce area for location 3": "select_the_workforce_area_for_location_3",
        "Name of Union 3": "name_of_union_3",
        "Contact name for Union 3": "contact_name_for_union_3",
        "Contact phone number for Union 3": "contact_phone_number_for_union_3",
        "Email address for Union 3": "email_address_for_union_3",
        "Address, City, ZIP for Union 3": "address_city_zip_for_union_3",
        "Include here any comments or additional details": "include_here_any_comments_or_additional_details",
        # This is for garbage, not legit crosswalk. You probably do not want to add here.
    }

    standardized_data = []
    for row in cleaned_data:
        row_dict = {}
        mangled = []
        for key in row:
            if (
                key not in header_crosswalk and key not in header_garbage
            ):  # Get all missing keys at once
                mangled.append(key)
        if len(mangled) > 0:
            logger.warning(f"Missing a bunch of keys: {'|'.join(mangled)}")

        for key, value in row.items():
            if (
                key not in header_crosswalk and key not in header_garbage
            ):  # If we've never seen this before
                logger.warning(f"Could not find {key} in header_crosswalk")
                logger.warning(row)
            if key not in header_garbage:  # if it's in the crosswalk, if it's legit
                standardized_key = header_crosswalk[key]
                row_dict[standardized_key] = value
        if len(row_dict["company"]) < 3 and row_dict["letter"] == "Avis Budget Group":
            row_dict["company"] = "Avis Budget Group"
        if len(row_dict["company"]) < 3:  # or len(row_dict['naics']) <5:
            logger.debug(f"Dropping row of questionable quality: {row_dict}")
        elif "begin_date" in row_dict and row_dict["begin_date"] == "Layoff Date(s)":
            logger.debug(f"Dropping row of questionable quality: {row_dict}")
        else:
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
    # logger.debug(table)
    # If a header list isn't provided, pull one out automatically
    if not header_list:
        # Pull out the header row
        # header_soup = table.find_all("tr")[1]
        header_soup = table.find_all("tr")[0]
        # Parse the header row into a list,
        # preserving its order in the sheet
        header_list = []
        for cellindex, cell in enumerate(header_soup.find_all("td")):
            cell_text = cell.text.strip()
            # Skip empty headers
            if cell_text:
                header_list.append(cell_text)
            if not cell_text and cellindex == 0:
                header_list.append("Company Name")

    # Loop through all the data rows, which start
    # after the header and the little bar
    tr_list = table.find_all("tr")[1:]
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
