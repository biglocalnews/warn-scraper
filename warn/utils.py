import csv
import logging
import os
import typing
from pathlib import Path

import requests
from retry import retry
from openpyxl import load_workbook

logger = logging.getLogger(__name__)


# The default home directory, if nothing is provided by the user
WARN_USER_DIR = Path(os.path.expanduser("~"))
WARN_DEFAULT_OUTPUT_DIR = WARN_USER_DIR / ".warn-scraper"

# Set the home directory
WARN_OUTPUT_DIR = Path(os.environ.get("WARN_OUTPUT_DIR", WARN_DEFAULT_OUTPUT_DIR))

# Set the subdirectories for other bits
WARN_CACHE_DIR = WARN_OUTPUT_DIR / "cache"
WARN_DATA_DIR = WARN_OUTPUT_DIR / "exports"
WARN_LOG_DIR = WARN_OUTPUT_DIR / "logs"


def create_directory(path: Path, is_file: bool = False):
    """Create the filesystem directories for the provided Path objects.

    Args:
        path (Path): The file path to create directories for.
        is_file (bool): Whether or not the path leads to a file (default: False)
    """
    # Get the directory path
    if is_file:
        # If it's a file, take the parent
        directory = path.parent
    else:
        # Other, assume it's a directory and we're good
        directory = path

    # If the path already exists, we're good
    if directory.exists():
        return

    # If not, lets make it
    logger.debug(f"Creating directory at {directory}")
    directory.mkdir(parents=True)


def write_rows_to_csv(output_path: Path, rows: list, mode="w"):
    """Write the provided list to the provided path as comma-separated values.

    Args:
        rows (list): the list to be saved
        output_path (Path): the Path were the result will be saved
        mode (str): the mode to be used when opening the file (default 'w')
    """
    create_directory(output_path, is_file=True)
    logger.debug(f"Writing {len(rows)} rows to {output_path}")
    with open(output_path, mode, newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def write_dict_rows_to_csv(output_path, headers, rows, mode="w", extrasaction="raise"):
    """Write the provided dictionary to the provided path as comma-separated values.

    Args:
        output_path (Path): the Path were the result will be saved
        headers (list): a list of the headers for the output file
        rows (list): the dict to be saved
        mode (str): the mode to be used when opening the file (default 'w')
        extrasaction (str): what to do if the if a field isn't in the headers (default 'raise')
    """
    create_directory(output_path, is_file=True)
    logger.debug(f"Writing {len(rows)} rows to {output_path}")
    with open(output_path, mode, newline="") as f:
        # Create the writer object
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction=extrasaction)
        # If we are writing a new row ...
        if mode == "w":
            # ... drop in the headers
            writer.writeheader()
        # Loop through the dicts and write them in one by one.
        for row in rows:
            writer.writerow(row)


def get_all_scrapers():
    """Get all the states and territories that have scrapers.

    Returns: List of lower-case post abbreviations.
    """
    this_dir = Path(__file__).parent
    scrapers_dir = this_dir / "scrapers"
    return sorted(
        p.stem for p in scrapers_dir.glob("*.py") if "__init__.py" not in str(p)
    )


@retry(tries=3, delay=15, backoff=2)
def get_url(
    url, user_agent="Big Local News (biglocalnews.org)", session=None, **kwargs
):
    """Request the provided URL and return a response object.

    Args:
        url (str): the url to be requested
        user_agent (str): the user-agent header passed with the request (default: biglocalnews.org)
        session: a session object to use when making the request. optional
    """
    logger.debug(f"Requesting {url}")

    # Set the headers
    if "headers" not in kwargs:
        kwargs["headers"] = {}
    kwargs["headers"]["User-Agent"] = user_agent

    # Go get it
    if session is not None:
        logger.debug(f"Requesting with session {session}")
        response = session.get(url, **kwargs)
    else:
        response = requests.get(url, **kwargs)
    logger.debug(f"Response code: {response.status_code}")

    # Verify that the response is 200
    assert response.ok

    # Return the response
    return response


def parse_excel(excel_path: Path, keep_header: bool = True) -> typing.List[typing.List]:
    """Parse the Excel file at the provided path.

    Args:
        excel_path (Path): The path to an XLSX file
        keep_header (bool): Whether or not to return the header row. Default  True.

    Returns: List of values ready to write.
    """
    # Open it up
    workbook = load_workbook(filename=excel_path)

    # Get the first sheet
    worksheet = workbook.worksheets[0]

    # Convert the sheet to a list of lists
    row_list = []
    for i, r in enumerate(worksheet.rows):
        # Skip the header row, if that's what the user wants
        if i == 0 and not keep_header:
            continue

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
