import logging
import os
import re
from datetime import datetime
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Louisiana Workforce Commission",
    "url": "https://www.laworks.net/Downloads/Downloads_WFD.asp",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Lousiana.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Fire up the cache
    cache = Cache(cache_dir)

    # The basic configuration for the scrape
    state_code = "la"
    base_url = "https://www.laworks.net/"
    file_base = "Downloads_WFD"

    # Download the root page
    url = f"{base_url}Downloads/{file_base}.asp"
    html = utils.get_url(url).text

    # Save it to the cache
    cache_key = f"{state_code}/{file_base}.html"
    cache.write(cache_key, html)

    # Parse out the links to WARN notice PDFs
    document = BeautifulSoup(html, "html.parser")
    links = document.find_all("a")

    all_rows = []

    for link in links:
        if "WARN Notices" in link.text:
            # Download the PDF
            pdf_url = f"{base_url}{link['href']}"
            pdf_path = _read_or_download(cache, state_code, pdf_url)

            # Process the PDF
            rows = _process_pdf(pdf_path)
            all_rows.extend(rows)

    # Insert a header row with clean column names.
    # We are here assuming that the columns don't change between years
    # and that one that contains "Employees Affected" will be clean.
    output_rows = [list(filter(_is_clean_header, all_rows))[0]] + list(
        filter(lambda row: not _is_header(row), all_rows)
    )

    # Write out to CSV
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path
    return data_path


def _append_contents_to_cells_in_row_above(rows: list, index: int, row: list) -> list:
    """
    Append the contents of a row to the contents of the cell above it.

    Keyword arguments:
    index -- the index of the row
    row -- the row to check
    rows -- the rows to append to
    """
    for column_index, cell in enumerate(row):
        if _cell_above_exists(column_index, rows):
            rows[len(rows) - 1][column_index].extend(cell)
    return rows


def _cell_above_exists(column_index: int, rows: list) -> bool:
    """
    Return True if the cell above the current cell exists.

    Keyword arguments:
    column_index -- the index of the column
    rows -- the rows to check
    """
    return column_index < len(rows[len(rows) - 1])


def _has_rows(rows: list) -> bool:
    """
    Determine if the table has rows.

    Keyword arguments:
    rows -- the rows to check

    Returns: True if the table has rows, False otherwise
    """
    return len(rows) > 0


def _is_first(index: int) -> bool:
    """
    Determine if a row is the first row in a table.

    Keyword arguments:
    index -- the index of the row

    Returns: True if the row is the first row in a table, False otherwise
    """
    return index == 0


def _is_mostly_empty(row: list) -> bool:
    """
    Check if a row has few populated cells. Used to determine if carried over from a previous page.

    Keyword arguments:
    row -- the row to check

    Returns: True if the row is mostly empty, False otherwise
    """
    return len(list(filter(pdfplumber.utils.extract_text, row))) <= 2


def _process_pdf(pdf_path):
    """
    Process a PDF file.

    Keyword arguments:
    pdf_path -- the path to the PDF file

    Returns: a list of rows
    """
    output_rows: list = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.debug_tablefinder().tables:
                for index, row in enumerate(table.rows):
                    cells = row.cells
                    row = [_extract_cell_chars(page, cell) for cell in cells]

                    # If the first row in a table is mostly empty,
                    # append its contents to the previous row
                    if (
                        _is_first(index)
                        and _is_mostly_empty(row)
                        and _has_rows(output_rows)
                    ):
                        output_rows = _append_contents_to_cells_in_row_above(
                            output_rows, index, row
                        )
                    # Otherwise, append the row
                    else:
                        output_rows.append(row)

    return _clean_rows(output_rows)


def _clean_rows(rows):
    """
    Clean up rows.

    Keyword arguments:
    rows -- the rows to clean

    Returns: the cleaned rows
    """
    output_rows = []

    for row in rows:
        output_row = []
        for column_index, chars in enumerate(row):
            text = _clean_text(pdfplumber.utils.extract_text(chars))

            # If we're on the first column, try to extract location and notes
            if _is_first(column_index):
                # Tries to extract a company name, appends it to the row
                company_name = _extract_company_name(chars)
                output_row.append(company_name)
                remaining_text = text.replace(company_name, "")

                # Tries to extract a note, typically UPDATE or WARN RESCINDED
                note = _extract_note(chars).strip()

                # Whatever is left is assumbed to be the location
                location = remaining_text.strip().replace(note, "")

                # Append the location and note to the row or headers for those
                if _is_header(output_row):
                    output_row.append("Location")
                    output_row.append("Note")
                else:
                    output_row.append(location)
                    output_row.append(note)
            else:
                # Appends the remaining text to the row
                output_row.append(text)

        output_rows.append(output_row)

    return output_rows


def _extract_cell_chars(page, bbox):
    """
    Extract the characters from a cell.

    Keyword arguments:
    page -- the page from which to extract the characters
    bbox -- the bounding box of the cell

    Returns: a list of characters
    """
    # If the bounding box is empty, append an empty list
    if bbox is None:
        return []

    # Expand the bounding box to ensure it encompasses the bottom line of text
    vertical_threshold = 5
    expanded_bbox = _vertically_expand_bounding_box(bbox, vertical_threshold)

    # Get the characters from the cell
    return page.within_bbox(expanded_bbox).chars


def _vertically_expand_bounding_box(bbox, increase):
    """
    Expand the bounding box by a given amount in the vertical direction.

    Keyword arguments:
    bbox -- the bounding box to expand
    increase -- the amount to expand the bounding box

    Returns: the expanded bounding box
    """
    return (
        bbox[0],
        bbox[1],
        bbox[2],
        bbox[3] + increase,
    )


def _read_or_download(cache: Cache, prefix: str, url: str) -> Path:
    """
    Read a file from the cache or downloads it.

    Keyword arguments:
    cache -- the cache to use
    prefix -- the prefix to use for the cache key
    url -- the URL to download

    Returns: the path to the file
    """
    file_name = os.path.basename(url)
    cache_key = f"{prefix}/{file_name}"

    exists = cache.exists(cache_key)
    year = _extract_year(file_name)
    current_year = datetime.now().year

    # Form a file path so we can read from the cache
    if exists and year < current_year - 1:
        return cache.path / cache_key

    return cache.download(cache_key, url)


def _extract_year(text: str) -> int:
    """
    Extract the year from a PDF file name.

    Keyword arguments:
    text -- the text to extract the year from

    Returns: the year
    """
    year_pattern = re.compile(r"\d{4}", re.IGNORECASE)
    year = re.search(year_pattern, text)

    if year is not None:
        return int(year.group(0))
    else:
        raise Exception(f"Could not extract year from {text}")


def _is_header(row: list) -> bool:
    """
    Determine if a row is a header row.

    Keyword arguments:
    row -- the row to check

    Returns: True if the row is a header row, False otherwise
    """
    return row[0].strip().lower() == "company name"


def _is_clean_header(row: list) -> bool:
    """
    Return true for a header with a clean column name.

    Keyword arguments:
    row -- the rows to check

    Returns: true if the row is a clean header
    """
    return _is_header(row) and "Employees Affected" in row


def _extract_note(chars) -> str:
    """
    Extract a note from a PDF cell.

    Keyword arguments:
    chars -- the characters to extract the note from

    Returns: the note
    """
    text = pdfplumber.utils.extract_text(chars)

    # Split text into lines
    lines = text.split("\n")

    notes = []

    for line in lines:
        note_pattern = r"((UPDATE.*|WARN RESCINDED))+"
        note = re.search(note_pattern, line, re.IGNORECASE)
        if note:
            notes.append(_clean_text(note[0]))

    return " ".join(notes)


def _extract_company_name(chars) -> str:
    """
    Extract the company name from a PDF cell.

    Keyword arguments:
    chars -- the characters to extract the company name from

    Returns: the company name
    """
    text = pdfplumber.utils.extract_text(chars)

    # Split text into lines
    lines = text.split("\n")

    # We're assuming first line is always part of a company name
    company_name = _clean_text(lines[0])

    # Try to extract bold text in the cell
    bold_text = _clean_text(_extract_bold_text(chars))
    remaining_bold_text = bold_text.replace(company_name, "").strip()

    # Loop through all but first and last lines
    for index, line in enumerate(lines[1:-1]):
        line_text = _clean_text(line)

        # If line is bolded or doesn't match a pattern
        # it's probably part of the company name
        if remaining_bold_text.startswith(line_text) or (
            bold_text == "" and index < 1 and not _is_location(line_text)
        ):
            company_name += f" {line_text}"

            remaining_bold_text = remaining_bold_text.replace(line_text, "").strip()
        # The first time we hit a line that doesn't match our expectations,
        # we assume we've reached the end of the company name
        else:
            break

    return company_name


def _is_location(text) -> bool:
    """
    Determine if text is likely to be a location.

    Keyword arguments:
    text -- the text to check

    Returns: True if the text is likely to be a location, False otherwise
    """
    location_pattern = r"(^\d+|Highway|Hwy|Offshore|Statewide)"
    return re.match(location_pattern, text, re.IGNORECASE) is not None


def _extract_bold_text(chars) -> str:
    """
    Extract the bold text from a PDF cell.

    Keyword arguments:
    chars -- the list of characters in the cell

    Returns: the bold text
    """
    bold_chars = [char["text"] for char in chars if "Bold" in char["fontname"]]
    bold_text = "".join(bold_chars)
    return bold_text


def _clean_text(text) -> str:
    """
    Clean up text from a PDF cell.

    Keyword arguments:
    text -- the text to clean

    Returns: the cleaned text
    """
    # Replace None with an empty string
    if text is None:
        return ""

    # Standardize whitespace
    clean_text = re.sub(r"\s+", " ", text).strip()

    return clean_text


if __name__ == "__main__":
    scrape()
