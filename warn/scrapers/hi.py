from pathlib import Path

from bs4 import BeautifulSoup

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
        if len(dates[i]) > 20:
            includes_date = False
            for j in [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]:
                if j in dates[i].split(" ")[0]:
                    dates[i] = (
                        dates[i].split(" ")[0]
                        + " "
                        + dates[i].split(" ")[1]
                        + " "
                        + dates[i].split(" ")[2]
                    )
                    includes_date = True
                elif j in dates[i].split(" ")[-3]:
                    dates[i] = (
                        dates[i].split(" ")[-3]
                        + " "
                        + dates[i].split(" ")[-2]
                        + " "
                        + dates[i].split(" ")[-1]
                    )
                    includes_date = True
            if not includes_date:
                dates[i] = "*Correction"

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
