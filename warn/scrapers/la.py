import json
import logging
import os
import re
from pathlib import Path

from bs4 import BeautifulSoup

from warn.pdfrodent import pdfrodent as pdfrodent

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs", "stucka"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Louisiana Workforce Commission",
    "url": "https://www.laworks.net/Downloads/Downloads_WFD.asp",
}

logger = logging.getLogger(__name__)

want_debugging_file = True


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

    headerfixes = {
        "Company Name": "company_original",
        "Notice Date": "date_notice",
        "Layoff Date": "date_action",
        "Employees Affected": "affected",
        "supplement_0": "notes",
        "Address": "address_original",
    }

    ignore = """
    # First handle the older files, if needed
    pdffiles = sorted(cache.files(subdir="la/", glob_pattern="*.pdf"))
    historicalneeded = False
    historicalfiles = []
    for myyear in range(2007, 2023 + 1):
        targeturl = f"https://www.laworks.net/Downloads/WFD/WarnNotices{myyear}.pdf"
        targetfilename = str(cache_dir / "la"/targeturl.split("/")[-1])
        historicalfiles.append(targetfilename)
        if targetfilename not in pdffiles:
            logger.debug(f"Missing {targetfilename} from collection of {' ... '.join(pdffiles)}")
            filebin, filehtml = utils.get_with_zyte(targeturl)
            cache.write_binary(targetfilename, filebin)
            historicalneeded = True

    if historicalneeded:
        logger.debug(f"Need to process historical records")
        historicallist = []
        historicaldebug = []
        for historicalfile in historicalfiles:
            locallist, localdebug = pdfrodent.parse_pdf(historicalfile, headerfixes)
            historicallist.extend(locallist)
            historicaldebug.extend(localdebug)

        with open(Path(cache_dir) / "la/historical.json", "w") as outfile:
            outfile.write(json.dumps(historicallist), indent=4*" ")

        if want_debugging_file:
            with open(Path(cache_dir) / "la/debugging-historical.txt", "w") as outfile:
                for row in historicaldebug:
                    outfile.write(json.dumps(row) + "\r\n")
    else:
        logger.debug(f"No historical data missing.")

    logger.debug(f"Fetching historical data")
    with open(Path(cache_dir) / "la/historical.json", "r") as infile:
        historicallist = json.loads(infile)
    logger.debug(f"{len(historicallist):,} historical items imported.")
    """

    # Download the root page
    url = f"{base_url}Downloads/{file_base}.asp"
    htmlbin, html = utils.get_with_zyte(url)

    # Save it to the cache
    cache_key = cache_dir / f"{state_code}/{file_base}.html"
    utils.create_directory(Path(cache_key), is_file=True)
    cache.write(cache_key, html)

    # Parse out the links to WARN notice PDFs
    document = BeautifulSoup(html, "html.parser")
    links = document.find_all("a")

    masterlist = []
    fulldebug = []

    for link in links:
        if "WARN Notices" in link.text:
            # Download the PDF
            pdf_url = f"{base_url}{link['href']}"
            rawbin, rawtext = utils.get_with_zyte(pdf_url)
            pdf_path = cache_dir / f"{state_code}/{os.path.basename(pdf_url)}"

            with open(pdf_path, "wb") as fp:
                fp.write(rawbin)

            # Process the PDF
            logger.debug(f"Attempting to parse {pdf_path}")
            locallist, localdebug = pdfrodent.parse_pdf(pdf_path, headerfixes)
            masterlist.extend(locallist)
            fulldebug.extend(localdebug)

    # Earlier versions assumed headers were the same. Let's not do that.
    # Identify all header elements, even in the ones we're about to remove.
    allheaders = set()

    ignore += """
    logger.debug(f"Folding in historical data")
    masterlist.extend(historicallist)
    """
    if ignore:
        logger.debug("Historical PDFs are not available to be incorporated.")

    # Add a couple columns we're sort of missing
    for rowindex, row in enumerate(masterlist):
        if "address_original" in row:
            masterlist[rowindex]["address"] = row["address_original"]
            masterlist[rowindex]["company"] = row["company_original"]
            # " ".join(row["_int_raw_fields"][0].split("\n")[0])

        else:
            firstcell = row["_int_raw_fields"][0]
            # Let's assume that in most cases the address begins on a new line with a number.
            # In those cases, stuff from before that will be the company name.
            # Stuff beginning with the number but not the new line will be the address.

            # In other cases, we'll have to assume the first line is the company name
            # and stuff on subsequent lines is the address.

            if re.findall(r"(\n\d+)", firstcell, re.MULTILINE):
                mysplit = re.findall(r"(\n\d+)", firstcell, re.MULTILINE)[0].replace(
                    "\n", ""
                )
                masterlist[rowindex]["company"] = (
                    firstcell.split(mysplit)[0].strip().replace("\n", ", ")
                )
                masterlist[rowindex]["address"] = (
                    mysplit
                    + " "
                    + mysplit.join(firstcell.split(mysplit)[1:]).replace("\n", ", ")
                )
            else:
                masterlist[rowindex]["company"] = row["_int_raw_fields"][0].split("\n")[
                    0
                ]
                masterlist[rowindex]["address"] = ", ".join(
                    row["_int_raw_fields"][0].split("\n")[1:]
                )

    for row in masterlist:
        for item in row:
            allheaders.add(item)
    text = ""
    for item in sorted(allheaders):
        text += f"\t\t'{item}': ,\n"
    with open(Path(cache_dir) / "la/allheaders.txt", "w") as outfile:
        outfile.write(text)

    if want_debugging_file:
        with open(Path(cache_dir) / "la/debugging.txt", "w") as outfile:
            for row in fulldebug:
                outfile.write(json.dumps(row) + "\r\n")

    targetfilename = data_dir / f"{state_code}.csv"
    logger.debug(f"Writing {len(masterlist):,} rows of data to {targetfilename}")
    utils.write_disparate_dict_rows_to_csv(targetfilename, masterlist)

    return targetfilename


if __name__ == "__main__":
    scrape()
