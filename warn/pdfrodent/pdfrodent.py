import json
import logging
import re

import camelot  # pip install camelot-py==1.0.9 for now

logger = logging.getLogger(__name__)


def clean_cell(text: str) -> str:
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


def clean_row(row: list):
    """Clean up text from a list of strings.

    args:
        row (list): list of strings
    returns:
        line (list): list of strings, each with minimal whitespace
    """
    line: list = []
    for cell in row:
        line.append(clean_cell(cell))
    return line


def is_empty(row: list) -> bool:
    """
    Check if a row has no populated cells.

    Keyword arguments:
    row -- the row to check

    Returns: True if the row is empty, False otherwise
    """
    return len(list(filter(None, row))) == 0


def is_mostly_empty(row: list) -> bool:
    """
    Check if a row has few populated cells. Used to determine if carried over from a previous page.

    Keyword arguments:
    row -- the row to check

    Returns: True if the row is mostly empty, False otherwise
    """
    return len(list(filter(None, row))) <= 2


def has_content(value):
    """Check if a particular value has any content, e.g. is it a null or an empty string."""
    if value is list:
        content = True
    elif value is dict:
        content = True
    elif value is None:
        content = False
    else:
        value = str(value).strip()
        if len(value) > 0:
            content = True
        else:
            content = False
    return content


def count_data_items(row: list, prefixes=None) -> int:
    """
    Count number of non-blank non-null data items in a row that aren't an internal variable.

    Args:
        row (list of dicts): The row to check
        prefixes (list) optional: If not provided, will skip data items beginning with ["int_", "_int"]. To empty pass an empty list.
    Returns:
        Integer of how many non-blank non-internal data items there are
    """
    good_items = 0
    if not prefixes:
        prefixes = ["int_", "_int_"]
    for field in row:
        goodfieldname = True
        for prefix in prefixes:
            if field.startswith(prefix):
                goodfieldname = False
        if goodfieldname:
            if has_content(row[field]):
                good_items += 1
    return good_items


def drop_thin_rows(rows: list, cutnumber: int, prefixes=None):
    """
    Drop rows with an improperly low count of valid entries, after filtering out prefixed rows of safe data.

    Args:
        row: List of dicts
        cutnumber: Cut rows with X or fewer full items. x + 1, then, would be the minimum count of good.
        prefixes: list, optional. If not provided will neglect to count data items beginning with ["int_", "_int_"]. To empty pass an empty list.
    Returns:
        line: List of dics
    """
    lines = []
    if not prefixes:
        prefixes = ["int_", "_int_"]
    for row in rows:
        if count_data_items(row, prefixes=prefixes) > cutnumber:
            lines.append(row)
    return lines


internal_documentation_such_as_it_is = """
OK, this is going to be messy. The higher-level overview:
We get lists of strings from the PDF, an ostensible PDF row.

Some of these lists are going to be headers. The headers, of course, need to be detected initially.

And sometimes the headers show up as their own table, with nothing else.
If this is the case, they need to be applied as the headers to subsequent tables.

But headers can also repeat across pages, so we need to detect them.

To add to the fun, each of these rows from the PDF may be just part of another logical row,
from when cells are divided horizontally to hold multiple data points.

We need to detect those fragmentary lines, mostly by checking to see if most cells are empty.

If they're a fragment of a header, we need to track it somehow and build a structure to hold the fragment.
And remember header fragments may occur on multiple pages with multipage headers.
That means we need to build an initial structure to hold the headers, then skip some rows if we see the header again.

For non-header fragments, we need to append the data to the previous line in an appropriate data structure.

But wait! There's more!

PDF data tends to be really dirty, lots of junky white space.

Some people will use multiline data to show multiple data points in a single cell, such as Company name<newline>, City, State ZIP.
If we strip off white space, we're losing a way to segregate and process that data later. So we can't clean it up until later.
Unless it's for fragmentary rows, because we need to know that they're fragmentary and white space will wreck the count.

And of course lots of rows are entirely white space, just blank data rows left in a PDF. Those we just drop.

To sum up:
Just about every PDF row can be
An orphaned header, alone in the table
A full header row
A fragmentary header
A full data row
A fragmentary data row
A blank row

We need many little trackers to go through here and figure out what we're looking at.

We need code to clean up whitespace in cells and rows.

We need a function to delete rows with fewer than a certain number of data points (e.g., contents of a summary table).

We need a function that allows us to standardize header names.

We probably want code that tells us what PDF this is pulled from, on which row.
"""


def parse_pdf(pdffile: str, field_fixes: dict | None = None):
    """Parse a PDF file to extract data from tables.

    Args:
        Filename (string)
        field_fixes (string or dict): If supplied, a dictionary of header lookup values with values of the target name

    Returns:
        filelist: A list of dictionaries of data rows keyed to headers
        filerowholder: Debugging data showing how row types were determined
    """
    if not field_fixes:
        logger.debug(
            "No 'field_fixes' variable submitted to pdfrodent.parse_pdf function."
        )
        field_fixes = {}
    else:
        logger.debug(f"{len(field_fixes):,} field_fixes to be used to clean headers.")
    filelist = []
    filerowholder = []
    logger.debug(f"Opening {pdffile} for PDF parsing")
    tables = camelot.read_pdf(pdffile, pages="all")
    orphanedheader = False
    orphanholder = None
    for tableindex, table in enumerate(tables):
        locallist: list = []
        logger.debug(f"Processing table {tableindex} of {pdffile}")
        filerowholder.append(f"Processing table {tableindex} of {pdffile}")
        rawheader = None
        headerfirst = []
        headersupplement: dict = {}
        isheader = True
        seendata = False
        logger.debug(
            f"Processing table {tableindex} with {len(table.rows)} of {pdffile}"
        )

        # If the table has only one row, it's a stray header and should be used with the next table.
        if len(table.rows) == 1:
            logger.debug("\tOrphaned header detected!")
            filerowholder.append("\tOrphaned header detected!")
            orphanedheader = True
            patchedheaders = []
            rawheader = table.data[0]
            for item in clean_row(rawheader):
                if item in field_fixes:
                    patchedheaders.append(field_fixes[item])
                else:
                    logger.debug(
                        f"New header type found: {item}, not in {' '.join(sorted(list(field_fixes.keys())))}"
                    )
                    patchedheaders.append(item)
            orphanholder = {
                "rawheader": rawheader,
                "patchedheaders": patchedheaders,
            }
            logger.debug(f"{orphanholder}")
            filerowholder.append(f"{orphanholder}")
        # If there are multiple rows, there are a bunch of possibilities we need to poke ...
        else:
            # If we have a header from a one-row table, prepare to use the orphaned header
            if orphanedheader:
                isheader = True
                rawheader = orphanholder["rawheader"]  # type: ignore
                headerfirst = orphanholder["patchedheaders"]  # type: ignore

            for rowindex, row in enumerate(table.data):
                filerowholder.append(row)
                line: dict = {}  # rows in, lines out
                # If it's the first row in a table and we don't have an orphaned header,
                # it's an index row
                if rowindex == 0 and not orphanedheader:
                    rawheader = row
                    patchedheaders = []
                    for item in clean_row(rawheader):
                        if item in field_fixes:
                            patchedheaders.append(field_fixes[item])
                        else:
                            logger.debug(
                                f"New header type found: {item}, not in {' '.join(sorted(list(field_fixes.keys())))}"
                            )
                            patchedheaders.append(item)
                    headerfirst = patchedheaders
                    isheader = True
                    filerowholder.append("\tIndex row!")

                elif row == rawheader:  # Later instance of a page header
                    isheader = True
                    filerowholder.append("\tRepeated header")

                # Drop blank rows entirely
                elif is_empty(clean_row(row)):
                    filerowholder.append("\tEmpty row")
                    pass

                # Handle fragmentary records
                elif is_mostly_empty(clean_row(row)):
                    filerowholder.append("\tMostly empty row!")
                    if not seendata:  # Is this part of the initial header?
                        filerowholder.append("\tMostly empty row, haven't seen data")
                        for cellindex, cell in enumerate(row):
                            cleancell = clean_cell(cell)
                            if len(cleancell) > 0:  # If we have good data
                                fieldname = f"supplement{cellindex}"
                                headersupplement[fieldname] = None  # type: ignore
                            isheader = False
                            orphanedheader = False

                    else:  # seenheader
                        if isheader:  # Supplement to a header on a latter page
                            filerowholder.append(
                                "\tMostly empty row, seems to be appending to a header"
                            )
                            for cellindex, cell in enumerate(row):
                                cleancell = clean_cell(cell)
                                if len(cleancell) > 0:  # If we have good data
                                    if cleancell not in headersupplement:
                                        headersupplement[cellindex] = headersupplement
                                        logger.debug(
                                            f"Added {cleancell} to headersupplement, which now holds: {headersupplement}"
                                        )
                            isheader = False

                        else:  # Not a header, have seenheader; must be a regular row supplement
                            orphanedheader = False
                            isheader = False
                            filerowholder.append(
                                "\tMostly empty row, seems to be detailed info for a regular row"
                            )
                            for cellindex, cell in enumerate(row):
                                cleancell = clean_cell(cell)
                                if len(cleancell) > 0:  # If we have good data
                                    if cellindex in headersupplement:
                                        fieldname = headersupplement[cellindex]  # type: ignore
                                    else:
                                        fieldname = f"supplement_{cellindex}"
                                        logger.warning(
                                            f"Found {fieldname} as {cleancell} but not located in supplemental headers: {headersupplement}"
                                        )
                                        if fieldname in field_fixes:
                                            logger.debug(
                                                f"Shifting cell with {fieldname} to {field_fixes[fieldname]}"
                                            )
                                            fieldname = field_fixes[fieldname]
                                    locallist[-1][
                                        fieldname
                                    ] = cleancell  # Add it to the previous line
                        isheader = False

                else:
                    # It's not an orphaned header
                    # It's not the initial header
                    # It's not a supplemental header
                    # It's not an empty row
                    # It's not a supplemental data row
                    # We ... actually have a regular data row here.
                    orphanedheader = False
                    filerowholder.append("\tSeems to be a regular row.")
                    isheader = False
                    seendata = True
                    for cellindex, cell in enumerate(row):
                        line[headerfirst[cellindex]] = clean_cell(cell)
                    filerowholder.append(f"\t\t{line}")
                    locallist.append(line)

            report = table.parsing_report

            for lineindex, line in enumerate(locallist):
                line["_int_accuracy"] = report["accuracy"]
                line["_int_pdf_filename"] = pdffile.split("/")[-1].split("\\")[-1]
                line["_int_page"] = report["page"]
                line["_int_table_number"] = report["order"]
                line["_int_raw_fields"] = json.dumps(list(line.values()))
                line["_int_data_items"] = count_data_items(line)  # type: ignore
                if "Event Number" in line:
                    line["Event Number"] = line["Event Number"].replace("\n", "")

                locallist[lineindex] = line  # Save it back

        filelist.extend(locallist)
    return (filelist, filerowholder)
