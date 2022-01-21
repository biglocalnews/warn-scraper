import logging
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = ["ydoc5212"]
__tags__ = ["google-sheets"]

logger = logging.getLogger(__name__)

# one set of fields per year, in order as listed on the year's document
FIELDS = [
    [
        "",
        "",
        "",
        "company",
        "industry",
        "",
        "",
        "",
        "",
        "address",
        "",
        "warn date",
        "",
        "layoffs",
        "temporary_layoffs",
        "furloughs",
        "",
        "",
        "layoff date",
    ],
    [
        "company",
        "industry",
        "layoffs",
        "local area",
        "warn date",
        "layoff date",
        "layoff reason",
        "attachment",
        "occupations",
        "",
        "",
        "",
    ],
    [
        "company",
        "layoffs",
        "local area",
        "warn date",
        "layoff reason",
        "occupations",
        "layoff date",
    ],
    ["company", "layoffs", "local area", "warn date", "layoff reason"],
    ["company", "layoffs", "local area", "warn date", "layoff reason"],
    ["company", "layoffs", "local area", "warn date", "layoff reason"],
    ["company", "layoffs", "local area", "warn date", "layoff reason"],
]
OUTPUT_HEADERS = [
    "company",
    "industry",
    "address",
    "local area",
    "warn date",
    "layoffs",
    "layoff date",
    "layoff reason",
    "attachment",
]


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Colorado.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    cache = Cache(cache_dir)

    # urls from 2021 to 2015
    urls = [
        "https://docs.google.com/spreadsheets/d/1HO8Fnm_4xey3Ctt6mYIig61Zx5iNq6_j_dlIaJvBS6o/edit#gid=1509741939",
        "https://docs.google.com/spreadsheets/d/1Km1mSUnCGE3EtZQTnZEUwxbdDTOcDZmNx6bviTwl2jI/edit#gid=0",
        "https://docs.google.com/spreadsheets/d/1GZEh1FUcHFfovdKeagTHFiv_P-PVVx64Bk4Szc963Gs/edit#gid=0",
        "https://docs.google.com/spreadsheets/d/1AsxrFpcg5nDdlezayogQf03Fq0Bkt6c34plqbEFxljI/edit#gid=0",
        "https://docs.google.com/spreadsheets/d/19YAbx8HAC9mfDbAkxVxBwEl8YCPGHhE91QHJAGi7R98/edit#gid=0",
        "https://docs.google.com/spreadsheets/d/1M-jYA2cSbehhp1pbpcAa900PtjAgktCHbU556cSjzc4/edit#gid=0",
        "https://docs.google.com/spreadsheets/d/1dpKX0g31Fkv8Hs3k3cVCJ19ce4RANNlYSCwpEQA2nrI/edit#gid=0",
    ]
    # convert google sheet into direct link to csv for downloading
    urls = [url.replace("/edit#gid=", "/export?format=csv&gid=") for url in urls]

    output_rows = []
    # scrape from most recent to oldest (2015)
    # TODO probably merge 2021 layoff fields into total layoffs
    for num, url in enumerate(urls):
        # TODO try to read from cache first
        csv_path = f"co/{num}.csv"
        cache.download(csv_path, url)
        rows_to_add = []
        for row_idx, row in enumerate(cache.read_csv(csv_path)):
            if row_idx == 0:
                # we are actually hard-coding headers for each year,
                # so this part is commented out.

                # only download headers once
                # if not HEADERS:
                #     HEADERS = row
                # else:
                #     pass
                pass
            else:
                # if a header is erroneously placed in the middle of the file
                # (this is the case with row 7 of 2017 data)
                if row[0] == "Company":
                    continue
                # ignore blank rows
                if row and row.count("") != len(row):
                    rows_to_add.append(row)
        # Convert rows to dicts, using each year's hard-coded FIELDS
        rows_as_dicts = [dict(zip(FIELDS[num], row)) for row in rows_to_add]
        output_rows.extend(rows_as_dicts)
        logger.info(f"Successfully scraped url {url}")

    output_csv = data_dir / "co.csv"
    utils.write_dict_rows_to_csv(
        output_csv, OUTPUT_HEADERS, output_rows, extrasaction="ignore"
    )

    return output_csv


if __name__ == "__main__":
    scrape()
