import typing
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from .. import utils


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Montana.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    response = utils.get_url(
        "https://wsd.dli.mt.gov/wioa/related-links/warn-notice-page"
    )
    data_file_name = _extract_file_name(response.text)
    data_url = f"https://wsd.dli.mt.gov/_docs/wioa/{data_file_name}"
    df = pd.read_excel(data_url, engine="openpyxl")
    output_file = data_dir / "mt.csv"
    df.to_csv(output_file, index=False)
    return output_file


def _extract_file_name(html):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find(id="boardPage").find_all("a")
    # Below URL will look like: ="../../_docs/wioa/warn-9-1-21.xlsx"
    return [
        link.attrs["href"]
        for link in links
        if link.attrs.get("href", "").endswith("xlsx")
    ][0].split("/")[-1]


if __name__ == "__main__":
    scrape()
