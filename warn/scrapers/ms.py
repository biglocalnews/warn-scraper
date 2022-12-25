from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["Ash1R"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Mississippi Department of Employment Security",
    "url": "https://mdes.ms.gov/information-center/warn-information/",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Iowa.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Grab the page
    page = utils.get_url("https://mdes.ms.gov/information-center/warn-information/")
    html = page.text

    # Write the raw file to the cache
    cache = Cache(cache_dir)
    cache.write("xx/yy.html", html)
    soup = BeautifulSoup(html, "html5lib")
    a = soup.select("a[href*=pdf]")
    alllinks = ["https://mdes.ms.gov/" + link["href"] for link in a]
    links = []
    pdf_list = []
    for link in alllinks:
        if "map" not in link:
            links.append(link)
    for i in links:
        cache_key = i.split("/")[-2] + i.split("/")[-1]
        if cache.exists(cache_key):
            pdf_file = cache_dir / cache_key
        else:
            pdf_file = cache.download(cache_key, i)
        pdf_list.append(pdf_file)

    headers = [
        "Date",
        "Company City (County) Zip",
        "Workforce Area",
        "Event Number",
        "NAICS Code - Description",
        "Type",
        "Date of Action",
        "Comments",
        "Affected",
    ]
    final_data = []
    for file in pdf_list:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_tables()
                if text == []:
                    continue
                for i in range(len(text)):
                    if text[i][0][0] != "" and text[i][0][0][0] == "D":
                        notices = text[i]
                        break
                startrow = 0
                end_table = False
                while notices[startrow][0] is None or "/" not in notices[startrow][0]:
                    startrow += 1
                    if startrow == len(notices):
                        end_table = True
                        break
                if end_table:
                    continue
                for row in range(startrow, len(notices) - 1, 2):
                    final = []

                    if notices[row][0] is None or "/" not in notices[row][0]:
                        continue

                    for i in notices[row]:
                        if i is not None:
                            final.append(i)

                    for i in notices[row + 1]:
                        if i is not None:
                            final.append(i.strip())
                    while len(final) != 9:
                        if "" in final:
                            final.remove("")
                        else:
                            break
                    final_data.append(final)

    # Set the path to the final CSV
    # We should always use the lower-case state postal code, like nj.csv
    output_csv = data_dir / "ms.csv"
    cleaned_data = [headers] + final_data
    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, cleaned_data)

    # Return the path to the final CSV
    return output_csv


if __name__ == "__main__":
    scrape()
