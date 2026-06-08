import json
import logging
from pathlib import Path

from pyquery import PyQuery as pq

from warn.pdfrodent import pdfrodent as pdfrodent

from .. import utils
from ..cache import Cache

__authors__ = ["Ash1R", "stucka"]
__tags__ = ["pdf"]
__source__ = {
    "name": "Mississippi Department of Employment Security",
    "url": "https://mdes.ms.gov/information-center/warn-information/",
}

logger = logging.getLogger(__name__)
want_debugging_file = True


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Mississippi.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)
    remoteurl = __source__["url"]
    urlprefix = remoteurl.split(".gov")[0] + ".gov"

    html = utils.get_url(remoteurl).text
    cache.write("ms/index.html", html)

    content = pq(html)("div#page_content")
    anchors = pq(content)("a")

    # Parse HTML to identify relevant PDFs
    urlswanted = []
    for anchor in anchors:
        href = pq(anchor).attr("href")
        remoteurl = href
        if "http" not in remoteurl:
            remoteurl = urlprefix + remoteurl
        if remoteurl.endswith(".pdf"):
            if not remoteurl.endswith("map.pdf"):
                urlswanted.append(remoteurl)

    # Get the files. The five first-listed files, we want fresh.
    # That should cover every quarter in the latest year, and one quarter of the previous year, at least.
    for i, urlwanted in enumerate(urlswanted):
        basefilename = urlwanted.split("/")[-1]
        localfilename = cache_dir / f"ms/{basefilename}"
        if i <= 4:  # Get the five newest files to ensure proper overlap
            logger.debug(f"Fetching fresh copy of {localfilename}")
            utils.save_if_good_url(localfilename, urlwanted)
        else:
            logger.debug(f"Getting copy of {localfilename} if needed")
            utils.fetch_if_not_cached(localfilename, urlwanted)

    pdffiles = sorted(cache.files(subdir="ms/", glob_pattern="*.pdf"))

    # HEY!!!!!!!!!!!! NEED to do something with this.
    headerfixes = {
        "Date of\nNotice": "date_notice",
        "Company Name\n(City) (County) (Zip)": "company_raw",
        "Workforce\nArea": "workforce_area",
        "Event\nNumber": "event_number",
        "NAICS CODE –\nDescription": "NAICS",
        "Type of\nAction\n#\nAffected": "action",
        "Date of\nAction": "date_effective",
        "Reason / Comments": "comments",
    }

    logger.debug(
        f"{len(headerfixes):,} headerfixes are drafted but NONE ARE IN USE, WHAT ARE YOU DOING"
    )

    masterlist = []
    rowholder = []
    for pdffile in pdffiles:
        locallist, localrows = pdfrodent.parse_pdf(pdffile)
        masterlist.extend(locallist)
        rowholder.extend(localrows)

    targetfilename = data_dir / "ms.csv"
    logger.debug(f"Found {len(masterlist):,} extracted rows from the PDFs.")
    cleaned = pdfrodent.drop_thin_rows(masterlist, 5)
    logger.debug(
        f"After filtering out thin rows, we have {len(masterlist):,} rows of data meeting standards."
    )
    # utils.write_disparate_dict_rows_to_csv(targetfilename, masterlist)
    utils.write_disparate_dict_rows_to_csv(targetfilename, cleaned)

    if want_debugging_file:
        with open(Path(cache_dir) / "ms/debugging.txt", "w") as outfile:
            for row in rowholder:
                outfile.write(json.dumps(row) + "\r\n")

    return targetfilename
