import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from dateutil.parser import parse

from .. import utils

__authors__ = ["Ash1R"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Workforce Development Hawaii",
    "url": "https://labor.hawaii.gov/wdc/real-time-warn-updates/",
}


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
    page = utils.get_url("https://labor.hawaii.gov/wdc/real-time-warn-updates/")
    soup = BeautifulSoup(page.text)
    tags = soup.select("p a[href*=pdf]")
    p_tags = [i.parent.get_text().replace("\xa0", " ").split("\n") for i in tags]
    clean_p_tags = [j for i in p_tags for j in i]

    dates = [k.split("–")[0] for k in clean_p_tags]
    headers = ["Company", "Date", "PDF url"]
    data = [headers]
    for i in range(len(dates)):

        parsed_date = parse(dates[i], default=datetime.datetime(1776, 1, 1), fuzzy=True)
        if parsed_date == datetime.datetime(1776, 1, 1):
            dates[i] = "Correction"
        else:
            dates[i] = parsed_date.date()

    for i in range(len(tags)):
        row = []
        url = tags[i].get("href")
        row.append(tags[i].get_text())

        row.append(dates[i])

        row.append(url)
        data.append(row)

    output_csv = data_dir / "hi.csv"
    utils.write_rows_to_csv(output_csv, data)
    return output_csv


if __name__ == "__main__":
    scrape()
