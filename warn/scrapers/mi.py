import json
import logging
from pathlib import Path

import requests
from pyquery import PyQuery as pq

from .. import utils
from ..cache import Cache

__authors__ = ["anikasikka", "stucka"]
__tags__ = ["html", "pdf", "json"]
__source__ = {
    "name": "Michigan Department of Technology, Management and Budget",
    "url": "https://www.michigan.gov/leo/bureaus-agencies/wd/data-public-notices/warn-notices",
}

logger = logging.getLogger(__name__)


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
    # Data from before a format change on 2025-11-25 is available archived at
    # https://storage.cloud.google.com/bln-data-public/warn-layoffs/mi-before-20251125.zip

    # human page at https://www.michigan.gov/leo/bureaus-agencies/wd/data-public-notices/warn-notices
    # That calls a JSON with a p=20 flag, which turns out to be pagination.
    # So if we mess with that flag ...
    sourcejson = "https://www.michigan.gov/leo/sxa/search/results/?s={8E97AB1D-D2D4-47F8-8CC4-3F1039C8854F}&itemid={BE81F7C2-36A8-4FDE-853C-B05B6E090055}&sig=&autoFireSearch=true&v={1FFFCC21-5151-4A2B-ABFC-F7FE4E5C9783}&p=54321&o=Created%20Date%20sort%2CDescending"

    headers = {"User-Agent": "Big Local News (biglocalnews.org)"}

    r = requests.get(sourcejson, headers=headers)

    # Save the semi-raw data
    cache = Cache()

    cache.write("raw/mi.json", json.dumps(r.json()))

    entries = r.json()["Results"]

    translations = {
        "Cities": "city",
        "City": "city",
        "Closure date": "date_close",
        "Commencing date": "date_start",
        "Counties": "county",
        "County": "county",
        "Includes the following": "includes",
        "Layoff (permanent) - City": "city",
        "Layoff (temporary) - City": "city",
        "Layoff - Cities": "city",
        "Layoff - City": "city",
        "Layoff date": "date_start",
        "Layoff dates": "date_start",
        "Layoff- City": "city",
        "Layoffs - Cities": "city",
        "Mass Layoff/Plant Closure - City": "city",
        "Number of jobs affected": "jobs",
        "Number of jobs impacted": "jobs",
        "Reduction in Hours - Cities": "city",
        "Total number of jobs impacted": "jobs",
        "Type of company action": "action",
    }

    textfixes = {
        "\u2013": "--",
        "\u2014": "--",
        "\u200b": "",
        "\u00a0": " ",
        "\u2039": " ",
        "\u2019": "'",
        "\u00e9": "e",
    }

    # Data looks like it'd be nicely separated by P tags. And it was. Mostly.
    # Some entries like the DTW North Partners have a single P tag, and then the data selements are separated only by BRs.
    # That means there's at least three formats out there.
    # So ... Let's start doing things by text transforms only.

    masterlist = []
    for entry in entries:
        line = {}
        gutsraw = pq(entry["Html"])("div.search-results__section-content")
        guts = gutsraw.text()
        for textfix in textfixes:
            guts = guts.replace(textfix, textfixes[textfix])
        guts = guts.splitlines()
        line["company"] = guts[0]
        link = pq(gutsraw)("a").attr("href")
        if "http" not in link:
            link = "https://www.michigan.gov" + link
        link = link.replace("\\", "")
        line["link"] = link

        extras = None
        for gut in guts[1:]:
            if ":" in gut:
                title = gut.split(":")[0]
                content = ":".join(gut.split(":")[1:]).strip()
                if title not in translations:
                    logger.warning(
                        f"!!!!!!!!!!  Missing a key in lookup table: {title}"
                    )
                line[translations[title]] = content
            else:
                if not extras:
                    extras = gut
                else:
                    extras += "!!!" + gut
        """
        Need to find a unique identifier here. Tried to build one but the MotorCity casino messed it up.
        Let's instead use the base PDF filename.

        urlparse weirdly doesn't have this.

        Using the full URL would be ... really unwieldy.

        ... but will actually be the right thing to do. Ack.


                    if "jobs" not in line:
                        jobs = ""
                    else:
                        jobs = line['jobs']
                    if "date_start" not in line:
                        date_start = ""
                    else:
                        date_start = line['date_start']

                    if not jobs:
                        line["jobs"] = f"jobs_{line['company']}_{date_start}"
                    if not "date_start":
                        line["date_start"] = f"date_{line['company']}_{jobs}"
        """
        # pdfname = line['link'].split("/")[-1].split("?")[0]
        if "link" not in line:
            logger.debug(f"Missing link somehow? {entry}")
        pdfname = line["link"]
        if "jobs" not in line:
            line["jobs"] = pdfname
        if "date_start" not in line:
            line["date_start"] = pdfname

        line["extras"] = extras
        masterlist.append(line)

    output_csv = data_dir / "mi.csv"

    utils.write_disparate_dict_rows_to_csv(output_csv, masterlist)

    # Return the path to the final CSV
    return output_csv


if __name__ == "__main__":
    scrape()
