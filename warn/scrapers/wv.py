from pathlib import Path

import pdfplumber

from .. import utils
from ..cache import Cache

__authors__ = ["Ash1R"]
__tags__ = ["html", "pdf"]
__source__ = {
    "name": "Workforce West Virginia",
    "url": "https://workforcewv.org/public-information/warn-notices/current-warn-notices",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from west virginia workforce site.

    It was a big pdf with all historical data,
    And I used pdfplumber to extract the tables
    And put them into wv.csv
    """
    cache = Cache(cache_dir)
    headers = [
        "Company",
        "Address",
        "Contact Information",
        "Region",
        "County",
        "Date",
        "Projected Date",
        "Type",
        "Number Affected",
    ]
    final_data = [headers]

    wv_pdf = cache.download(
        "WV_WARN_Notices_3-1-11_to_3-22-22.",
        "https://workforcewv.org/images/files/PublicInfo/WV_WARN_Notices_3-1-11_to_3-22-22.pdf",
    )
    with pdfplumber.open(wv_pdf) as pdf:
        for i in pdf.pages:
            tables = i.find_tables()
            for j in tables:
                data = j.extract(x_tolerance=3, y_tolerance=3)
                company = ""
                companydone = False
                row = []
                for k in range(len(data)):
                    if data[k][0] is not None:
                        if (
                            (data[k][0].strip() == "Contact Information")
                            or (data[k][0].strip() == "Region")
                            or (data[k][0].strip() == "County")
                            or (data[k][0].strip() == "Date of Notice")
                            or (data[k][0].strip() == "Projected Date")
                            or (data[k][0].strip() == "Closure/Mass Layoff")
                            or (data[k][0].strip() == "Number Affected")
                        ):
                            row.append(data[k][1].strip())

                        elif data[k][0].strip() == "Address":
                            if not companydone:
                                row.append(company)
                                companydone = True
                            row.append(data[k][1].strip())

                        elif data[k][0].strip() == "Company":
                            company = company + data[k][1].strip()

                    elif ((data[k][0] is None) and (k != 0)) or (
                        data[k][0] == "None" and k != 0
                    ):
                        for p in range(1, len(data[k])):
                            if data[k][p] is not None:
                                company = company + ", " + data[k][p].strip()

                final_data.append(row)

    output_csv = data_dir / "wv.csv"
    utils.write_rows_to_csv(output_csv, final_data)
    return output_csv


if __name__ == "__main__":
    scrape()
