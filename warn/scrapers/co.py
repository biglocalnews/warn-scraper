from pathlib import Path

from .. import utils
from ..cache import Cache
from bs4 import BeautifulSoup
import re

__authors__ = ["anikasikka"]
__tags__ = ["html"]
__source__ = {
    "name": "Colorado Department of Labor and Employment",
    "url": "https://cdle.colorado.gov/employers/layoff-separations/layoff-warn-list",
}



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
    # Grab the page
    page = utils.get_url("https://cdle.colorado.gov/employers/layoff-separations/layoff-warn-list")
    html = page.text

    # Write the raw file to the cache
    cache = Cache(cache_dir)
    cache.write("co/main/source.html", html)

    # Setting the headers to centralize among archived and new data
    cleaned_data = []

    # Parses the current year's data into a CSV file
    soup = BeautifulSoup(html, "html5lib")
    current_link = str(soup.find("a", class_="btn btn-primary")).split("\"")[3]

    current_page = utils.get_url(current_link)
    current_html = current_page.text

    soup_current = BeautifulSoup(current_html, "html5lib")

    for rows in soup_current.find(class_="waffle").find_all("tr"):
        vals = []
        scrape_spreadsheet(rows, vals)
        if (len(vals) == 0):
            continue
        cleaned_data.append(vals)

    #Goes through the accordion links to get past data 
    new_vals = []
    main = soup.find_all('dl')
    for item in main: 
        my_list = item.find('ul')
        for li in my_list.find_all('li'):
            link = (str)(li).split("\"")[1]
            archived_page = utils.get_url(link)
            archived_html = archived_page.text
            soup_archived = BeautifulSoup(archived_html, "html5lib")
            for rows in soup_archived.find(class_="waffle").find_all("tr"):
                vals = []
                scrape_spreadsheet(rows, vals)
                if (len(vals) == 0): 
                    continue
                cleaned_data.append(vals)
    
    # Set the path to the final CSV
    # We should always use the lower-case state postal code, like nj.csv
    output_csv = data_dir / "co.csv"

    # Write out the rows to the export directory
    utils.write_rows_to_csv(output_csv, cleaned_data)

    # Return the path to the final CSV
    return output_csv


if __name__ == "__main__":
    scrape()

# Scrapes the google spreadsheet
def scrape_spreadsheet(rows, vals):
    for i, data in enumerate(rows.find_all("td")):
        data = (str)(data)
        data = re.sub("\<.*?\>","", data)
        vals.append(data)


