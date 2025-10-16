#!/usr/bin/env python

import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = [
    "stucka",
]
__tags__ = [
    "html",
]
__source__ = {
    "name": "Pennsylvania Department of Labor and Industry",
    "url": "https://www.pa.gov/agencies/dli/programs-services/workforce-development-home/warn-requirements/warn-notices",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Pennsylvania.

    Arguments:
    output_dir -- the Path were the result will be saved

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get the latest data
    cache = Cache(cache_dir)

    remoteurl = "https://www.pa.gov/agencies/dli/programs-services/workforce-development-home/warn-requirements/warn-notices"

    response = utils.get_url(remoteurl)

    html = response.text

    cache.write("pa/pa.html", response.text)

    # Clean up some garbage characters
    textfixes = {
        "# AFFECTED": "AFFECTED",
        "\u2013": "--",
        "\u200b": "",
        "\u00a0": " ",
        "\u2039": " ",
        "\u2019": "'",
    }

    for textfix in textfixes:
        html = html.replace(textfix, textfixes[textfix])

    soup = BeautifulSoup(html, "html.parser")

    entries = soup.find_all("div", class_="cmp-accordion__item")

    masterlist = []

    logger.debug(
        f"Found {len(entries):,} potential entries. (There will be fewer finalists.) "
    )

    for entry in entries:
        # print(str(entry))
        if "cmp-accordion__item" not in str(
            entry.decode_contents()  # innerHTML
        ):  # Find items not holding other items
            line = {}
            # The data is poorly structured; this seems to have an error rate of less than 1%.
            # The title's easy to get.
            # The rest of the details ("deets" are pulled apart by splitting lines.
            # Some have clear headers. Some without headers get folded up into the previous line.
            # That functionality allows all the dates of multiphase layoffs to be kept together.

            line["Company"] = (
                entry.find("span", class_="cmp-accordion__title").get_text().strip()
            )
            blob = entry.find("div", class_="text").get_text().strip()
            address = blob.split("COUNT")[0].strip()

            deets = "COUNT" + "COUNT".join(blob.split("COUNT")[1:])  # type: ignore
            deets = deets.split("\n")  # type: ignore
            line["addressfull"] = address.replace("\n", ", ")
            lastkey = None
            for deet in deets:
                if "PHASE" in deet.upper():
                    if len(line[lastkey]) > 0:  # type: ignore
                        line[lastkey] += " ... "  # type: ignore
                    line[lastkey] += deet.strip()  # type: ignore
                # elif ":" in deet and "Ending:" not in deet:
                elif ":" in deet and not deet.upper().startswith("ENDING"):
                    key = deet.split(":")[0]
                    if key == "COUNTIES":
                        key = "COUNTY"
                    value = ": ".join(deet.split(":")[1:]).strip()
                    line[key] = value
                    lastkey = key
                else:  # No colon in deet and no Phase
                    if len(line[lastkey]) > 0:  # type: ignore
                        line[lastkey] += " ... "  # type: ignore
                    line[lastkey] += deet.strip()  # type: ignore

            masterlist.append(line)

    # Now need to standardize these headers, and might as well make them meet some semblance of a standard.
    crosswalk = {
        "COUNTIES": "county",
        "COUNTY": "county",
        "Company": "company",
        "addressfull": "addressfull",
        "AFFECTED": "jobs",
        "EFFECTIVE DATE": "date_effective",
        "EFFECTIVE DATES": "date_effective",
        "CLOSURE OR LAYOFF": "closure_or_layoff",
    }

    tallies = {}
    for row in masterlist:
        for entry in row:
            if entry not in tallies:
                tallies[entry] = 0
            tallies[entry] += 1

    logger.debug("Showing all potential keys found before standardization")
    for entry in tallies:
        logger.debug(f"\t{entry}: {tallies[entry]}")

    # Now, standardize the keys.
    templist = masterlist
    masterlist = []
    for row in templist:
        line = {}
        for item in row:
            if item not in crosswalk:
                logger.error(f"Failed to find a matching crosswalk term for {item}")
            else:
                line[crosswalk[item]] = row[item]
        masterlist.append(line)

    masterlist.reverse()  # Flip into reverse chronological order

    # Write out the results
    data_path = data_dir / "pa.csv"
    utils.write_disparate_dict_rows_to_csv(data_path, masterlist)

    # Pass it out
    return data_path


if __name__ == "__main__":
    scrape()
