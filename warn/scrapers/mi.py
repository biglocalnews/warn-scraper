import re
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["anikasikka"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Michigan Department of Technology, Management and Budget",
    "url": "https://milmi.org/warn/",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Michigan.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Grabs the main page with the current year's data
    current_page = utils.get_url("https://milmi.org/warn/")
    current_html = current_page.text
    # Grabs the WARN archive years html page with previous data
    archive_web_page = utils.get_url("https://milmi.org/warn/archive")
    archive_web_html = archive_web_page.text
    # Write the raw current year's file to the cache
    cache = Cache(cache_dir)
    cache.write("mi/current.html", current_html)

    # Write the archived web data to the cache
    cache = Cache(cache_dir)
    cache.write("mi/archived.html", archive_web_html)

    headers = [
        "Company Name",
        "City",
        "Date Received",
        "Incident Type",
        "Number of Layoffs",
    ]
    cleaned_data = [headers]

    # Parse current year's html file
    soup_current = BeautifulSoup(current_html, "html5lib")
    cleaned_data += _parse_html_table(soup_current.find(class_="tablewarn"))

    # Parse archived web data file
    soup_archive = BeautifulSoup(archive_web_html, "html5lib")
    cleaned_data += _parse_html_table(soup_archive)

    # Parse out PDF links for downloading
    pdf_list = []
    for link in soup_archive.select("a[href$='.pdf']"):
        # Grab the text
        link_text = link.text.strip()
        # Only keep the ones that have a four digit year in the text
        if not re.match(r"\d{4}", link_text):
            continue

        # Put the URL together
        pdf_url = f"https://milmi.org/_docs/publications/warn/warn{link_text}.pdf"

        # Download it
        cache_key = f"mi/{link_text}.pdf"
        if cache.exists(cache_key):
            pdf_file = cache_dir / cache_key
        else:
            pdf_file = cache.download(cache_key, pdf_url)
        pdf_list.append(pdf_file)

    # parse pdf data
    pdf_data = []

    # Parse the pdfs from 2007-2015
    for file in range(len(pdf_list) - 9, len(pdf_list))[::-1]:
        with pdfplumber.open(pdf_list[file]) as pdf:
            for i in pdf.pages:
                pdf_data += process_pdf_2(i.extract_text())

    # Parse pdfs from 2000-2006, which use a different type of spacing
    for file in range(len(pdf_list) - 9)[::-1]:
        with pdfplumber.open(pdf_list[file]) as pdf:
            for i in pdf.pages:
                pdf_data += process_pdf_1(i.extract_text())

    cleaned_data += pdf_data

    # Set the path to the final CSV
    # We should always use the lower-case state postal code, like nj.csv
    output_csv = data_dir / "mi.csv"

    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, cleaned_data)

    # Return the path to the final CSV
    return output_csv


def process_pdf_1(txt):
    """Process the 2000-2006 pdfs."""
    # split at newline, remove space placeholders, parts that aren't layoff data
    txt = txt.split("\n")
    txt = [i.replace("\xa0", " ").replace("\xad", " ") for i in txt]
    txt = txt[5:-5]

    # contains all the data for the page
    ans = []

    for row in txt:

        # used later to check if data is damaged
        broken = False
        # the final processed row goes here
        final = []

        # the furthest the company name column ends is at index 35
        compname = 35

        try:
            # However, sometimes it ends before that,
            # so we start at index 35 and go back until we hit a space
            while row[compname] != " ":
                # if not space is found, the row is smushed together
                if compname == 0:
                    broken = True
                    break
                compname -= 1
            if broken:
                txt.remove(row)
                continue
        except Exception:
            # if this fails, the data is damaged (it fails on about 5 rows)
            txt.remove(row)
            continue

        # add company name to final row
        final.append(row[: compname + 1])

        # Usually, the city name ends 21 characters after the company name
        # this isn't always the case, so we do what we did with company column
        cityname = compname + 21
        try:
            while row[cityname] != " ":
                broken = False
                if cityname == 0:
                    broken = True
                cityname -= 1
            if broken:
                txt.remove(row)
                continue
        except Exception:
            # if it fails, the data is damaged (it only fails on two)
            txt.remove(row)
            continue

        # add city name to final row
        final.append(row[compname + 1 : cityname])

        # temp contains the test of the string
        # which has date, event type, and number affected in that order
        temp = row[cityname + 1 :]

        # split to get date, event type, and number affected seperately
        temp = temp.split()

        # they use numbers instead of these words in some of the pdf
        if temp[1] == "1":
            temp[1] = "Plant Closing"
        elif temp[1] == "2":
            temp[1] = "Mass Layoff"
        elif temp[1] == "3":
            temp[1] = ""
        elif temp[1] == "4":
            temp[1] = ""

        # add date, event type, and number affected to final row
        for j in temp:
            final.append(j)

        # eliminate extra space
        final = [row.strip() for row in final]

        # see function
        final = handle_edge_cases(final)

        # add row to page
        ans.append(final)
    return ans


def process_pdf_2(txt):
    """Process 2007-2015 pdfs."""
    # split at newline
    txt = txt.split("\n")
    ans = []
    for i in txt:
        final = []
        # split at spaces, which are used as column divders
        raw = i.split(" ")
        # remove space placeholders
        final = [j.replace("\xa0", " ").replace("\xad", " ") for j in raw]

        # removing edge cases such as the "Notes:" section and blank lines
        if (
            len(final) == 5
            and (final[0] not in ["Company", "Company Name"])
            and final[1] != "Received"
            and final != [" ", " ", " ", " ", " "]
        ):
            ans.append(final)
        # accounting for the 2008-2009 minor format changes
        if len(final) == 6:
            if (final[2][-4:] == "2008" or final[2][-4:] == "2009") and (
                final[0] != "January 1 through December 31:"
            ):
                final.pop(-1)
                ans.append(final)

    return ans


# there are around 15 lines with unique spacing issues
# there doesn't seem to be a pattern to them,
# so I just fixed them manually
# there may be a more elegant solution
def handle_edge_cases(row):
    """Handle edge cases in 2000-2006 pdfs."""
    if row[0] == "General Motors Nao Orion AsseOrion":
        row[1] = "Orion"
        row[0] = row[0][-5:]
    if row[1] == "LifDetroit":
        row[1] = "Detroit"
    if row[1] == "ILapeer":
        row[1] = "Lapeer"
    if row[0] == "Standard Federal Bank #320     Troy":
        row[1] = "Troy"
        row[0] = "Standard Federal Bank #320"
    if row[0] == "Standard Federal Bank #340     Troy":
        row[1] = "Troy"
        row[0] = "Standard Federal Bank #340"
    if row[1] == "IFlint":
        row[1] = "Flint"
    if row[1] == "DivisioJackson":
        row[1] = "Jackson"
    if row[1] == "IncWyoming":
        row[1] = "Wyoming"
    if row[0] == "Michigan Machine And EngineerFenton":
        row[1] = "Fenton"
        row[0] = row[0][-6:]
    if row[1] == "CompDearborn Heights":
        row[1] = "Dearborn Heights"
    if row[1] == "InPetersburg":
        row[1] = "Petersburg"
    if row[0] == "Asplundh Tree Company #93     Wixom":
        row[0] = row[0][-5:]
        row[1] = "Wixom"
    if row[0] == "Asplundh Tree Company #43     Mt.":
        row[0] = "Asplundh Tree Company #43"
        row[1] = "Mt. Clemens"
    if row[0] == "Asplundh Tree Company #843   Howell":
        row[0] = "Asplundh Tree Company #843"
        row[1] = "Howell"
    if row[1] == "RegionaSaginaw":
        row[1] = "Saginaw"
    if row[0] == "Robert Bosch Corp. Chassis DivisSi":
        row[0] = "Robert Bosch Corp. Chassis Division"
        row[1] = "St. Joseph"
    if row[0] == "Magna / Cosma Body & Chassis Troy":
        row[0] = row[0][-4:]
        row[1] = "Troy"
    if row[1] == "Corp.Flint":
        row[1] = "Flint"
    if row[1] == "Inc.Howell":
        row[1] = "Howell"
    return row


def _parse_html_table(soup):
    black_list = [
        "TOTAL:",
        "Number of notices received Y-T-D",
        "Total Layoffs:",
        "Notes:",
        "",
    ]
    row_list = []
    # Loop through all the rows ...
    for rows in soup.find_all("tr"):
        # Grab all the cells
        vals = []
        for data in rows.find_all("td"):
            vals.append(data.text.strip())

        # Quit if there's nothing
        if not vals:
            continue

        # If this is a blacklisted row, like the total row, skip it
        if vals[0] in black_list:
            continue

        # If we get this far, keep it
        row_list.append(vals)

    # Return the result
    return row_list


if __name__ == "__main__":
    scrape()
