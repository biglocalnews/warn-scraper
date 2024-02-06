import datetime
import logging
from pathlib import Path
from time import sleep
from urllib.parse import quote

from bs4 import BeautifulSoup

from .. import utils

__authors__ = ["Ash1R", "stucka"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Workforce Development Hawaii",
    "url": "https://labor.hawaii.gov/wdc/real-time-warn-updates/",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Hawaii.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)
    Returns: the Path where the file is written
    """
    # Google Cache is a backup if the state re-implements its JS-enabled browser equivalent
    usegooglecache = False
    cacheprefix = "https://webcache.googleusercontent.com/search?q=cache%3A"

    firstpageurl = "https://labor.hawaii.gov/wdc/real-time-warn-updates/"
    if usegooglecache:
        firstpageurl = cacheprefix + quote(firstpageurl)

    firstpage = utils.get_url(firstpageurl)
    soup = BeautifulSoup(firstpage.text, features="html5lib")
    pagesection = soup.select("div.primary-content")[0]
    subpageurls = []
    for atag in pagesection.find_all("a"):
        href = atag["href"]
        if href.endswith("/"):
            href = href  # [:-1]
        subpageurl = href
        if usegooglecache:
            subpageurl = cacheprefix + quote(subpageurl)
        subpageurls.append(subpageurl)

    masterlist = []
    headers = ["Company", "Date", "PDF url", "location", "jobs"]
    #    data = [headers]
    # lastdateseen = "2099-12-31"

    for subpageurl in reversed(subpageurls):
        sleep(2)
        # Conditionally here, we want to check and see if we have the old cached files, or if the year is current or previous.
        # Only need to download if it's current or previous year.
        # But do we care enough to implement right now?

        logger.debug(f"Parsing page {subpageurl}")
        page = utils.get_url(subpageurl)
        soup = BeautifulSoup(page.text, features="html5lib")
        if subpageurl.endswith("/"):
            subpageurl = subpageurl[:-1]  # Trim off the final slash, if there is one
        pageyear = subpageurl.split("/")[-1][:4]

        # There are at least two formats for Hawaii. In some years, each individual layoff is in a paragraph tag.
        # In others, all the layoffs are grouped under a single paragraph tag, separated by <br>
        # BeautifulSoup converts that to a <br/>.
        # But the call to parent also repeats a bunch of entries, so we need to ensure they're not.
        # So in more recent years, finding the parent of the "p a" there find essentially the row of data.
        # In the older years, the parent is ... all the rows of data, which gets repeated.
        # So take each chunk of data, find the parent, do some quality checks, clean up the text,
        # don't engage with duplicates.

        selection = soup.select("p a[href*=pdf]")
        rows = []
        for child in selection:
            parent = child.parent
            for subitem in parent.prettify().split("<br/>"):
                if len(subitem.strip()) > 5 and ".pdf" in subitem:
                    subitem = subitem.replace("\xa0", " ").replace("\n", "").strip()
                    row = BeautifulSoup(subitem, features="html5lib")
                    if row not in rows:
                        rows.append(row)

        for row in rows:
            line: dict = {}
            for item in headers:
                line[item] = None
            graftext = row.get_text().strip()
            tempdate = graftext

            # Check to see if it's not an amendment, doesn't have 3/17/2022 date format
            # Most dates should be like "March 17, 2022"
            if pageyear in tempdate and f"/{pageyear}" not in tempdate:
                try:
                    tempdate = (
                        graftext.strip().split(pageyear)[0].strip() + f" {pageyear}"
                    )
                except ValueError:
                    print(f"Date conversion failed on row: {row}")

            line["Date"] = tempdate

            try:
                parsed_date = datetime.datetime.strptime(
                    tempdate, "%B %d, %Y"
                ).strftime("%Y-%m-%d")
                line["Date"] = parsed_date
            except ValueError:
                logger.debug(f"Date error: '{tempdate}',  leaving intact")

            line["PDF url"] = row.select("a")[0].get("href")
            line["Company"] = row.select("a")[0].get_text().strip()

            # Before 2024, the a href contained the company name. In 2024, it's the date.
            if line["Company"] == tempdate:
                line["Company"] = row.get_text().strip().replace(tempdate, '').replace('–', '').strip()
            masterlist.append(line)

    if len(masterlist) == 0:
        logger.error(
            "No data scraped -- anti-scraping mechanism may be back in play -- try Google Cache?"
        )
    output_csv = data_dir / "hi.csv"
    utils.write_dict_rows_to_csv(output_csv, headers, masterlist)
    return output_csv


if __name__ == "__main__":
    scrape()
