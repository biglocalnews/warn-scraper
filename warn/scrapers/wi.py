import csv
import logging
import re
import requests

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f"{output_dir}/wi.csv"
    years = [2016, 2017, 2018, 2019]
    url = "https://sheets.googleapis.com/v4/spreadsheets/1cyZiHZcepBI7ShB3dMcRprUFRG24lbwEnEDRBMhAqsA/values/Originals?key=AIzaSyDP0OltIjcmRQ6-9TTmEVDZPIX6BSFcunw"
    response = requests.get(url)
    logger.debug(f"Page status is {response.status_code} for {url}")
    data = response.json()
    # find header
    headers = data["values"][0]
    output_header = headers[3:len(headers) - 1]
    output_rows = []
    for row in data["values"][1:len(data["values"])]:
        output_row = row[3:len(row)]
        if output_row and output_row[-1].strip() == "Y":
            # remove erroneous 'Y' fields
            output_row = output_row[:-1]
        output_rows.append(output_row)
    # save header
    with open(output_csv, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
        writer.writerows(output_rows)
    for year in years:
        url = "https://dwd.wisconsin.gov/dislocatedworker/warn/{}/default.htm".format(
            year
        )
        page = requests.get(url)
        logger.debug(f"Page status is {page.status_code} for {url}")
        soup = BeautifulSoup(page.text, "html.parser")
        tables = soup.find_all("table")  # output is list-type
        for table in tables:
            output_rows = []
            for table_row in table.find_all("tr"):
                columns = table_row.find_all("td")
                output_row = []
                for column in columns:
                    entry = column.text
                    # remove trailing characters after LayoffBeginDate
                    if re.match(r"^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", entry):
                        entry = re.sub(r"(?<=[0-9]{4}).*", "", entry)
                    output_row.append(entry)
                output_row = [x.strip() for x in output_row]
                # filter "Updates to Previously Filed Notices"
                if output_row and len(output_row) > 2:
                    output_rows.append(output_row)
            if len(output_rows) > 0:
                try:
                    with open(output_csv, "a", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(output_rows)
                except UnicodeEncodeError:
                    with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(output_rows)
    return output_csv
