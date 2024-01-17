import datetime
import logging
from pathlib import Path
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
    cacheprefix = "https://webcache.googleusercontent.com/search?q=cache%3A"    # Use Google Cache, per #600

    firstpage = utils.get_url(cacheprefix + quote("https://labor.hawaii.gov/wdc/real-time-warn-updates/"))
    soup = BeautifulSoup(firstpage.text, features="html5lib")
    pagesection = soup.select("div.primary-content")[0]
    subpageurls = []
    for atag in pagesection.find_all("a"):
        href = atag["href"]
        if href.endswith("/"):
            href = href         # [:-1]
        subpageurls.append(cacheprefix + quote(href))

    headers = ["Company", "Date", "PDF url", "location", "jobs"]
    data = [headers]
    # lastdateseen = "2099-12-31"

    for subpageurl in reversed(subpageurls):
        # Conditionally here, we want to check and see if we have the old cached files, or if the year is current or previous.
        # Only need to download if it's current or previous year.
        # But do we care enough to implement right now?

        logger.debug(f"Parsing page {subpageurl}")
        page = utils.get_url(subpageurl)
        soup = BeautifulSoup(page.text, features="html5lib")
        pageyear = subpageurl.split("/")[-1][:4]
        tags = soup.select("p a[href*=pdf]")
        p_tags = [i.parent.get_text().replace("\xa0", " ").split("\n") for i in tags]
        clean_p_tags = [j for i in p_tags for j in i]

        dates = [k.split("–")[0].strip() for k in clean_p_tags]
        for i in range(len(dates)):
            try:
                tempdate = dates[i].split(pageyear)[0].strip() + f" {pageyear}"
                parsed_date = datetime.datetime.strptime(
                    tempdate, "%B %d, %Y"
                ).strftime("%Y-%m-%d")
                dates[i] = parsed_date
            #    lastdateseen = parsed_date

            # Disabling amendment automation to shift fixes into warn-transformer instead.
            # If this needs to come back, uncomment the lastseendate references
            # then rebuild the below section as an else
            except ValueError:
                logger.debug(f"Date error: {dates[i]}, leaving intact")
        #                if "*" in dates[i]:
        #                    logger.debug(
        #                        f"Date error: {dates[i]} as apparent amendment; saving as {lastdateseen}"
        #                    )
        #                    dates[i] = lastdateseen
        #                else:

        for i in range(len(tags)):
            row = []
            url = tags[i].get("href")
            row.append(tags[i].get_text())

            row.append(dates[i])

            row.append(url)
            row.append(None)     # location
            row.append(None)     # jobs
            data.append(row)

    output_csv = data_dir / "hi.csv"
    utils.write_rows_to_csv(output_csv, data)
    return output_csv


if __name__ == "__main__":
    scrape()
