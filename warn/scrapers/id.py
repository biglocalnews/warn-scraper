import logging
import random
import re
import typing
from pathlib import Path

import pdfplumber
import requests

from .. import utils

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Idaho.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """

    # There's a numeric parameter called v on this PDF URL that updates
    # from time to time. Suspect this is a cache-buster. We're using a
    # random number instead.
    cache_buster = random.randrange(1, 10000000000)

    url = f"https://www.labor.idaho.gov/dnn/Portals/0/Publications/WARNNotice.pdf?v={cache_buster}"

    cache_state = Path(cache_dir, "id")
    cache_state.mkdir(parents=True, exist_ok=True)

    pdf_file = f"{cache_state}/WARNNotice.pdf"

    # verify=False because there's a persistent cert error
    # we're working around.
    response = requests.get(url, verify=False)
    with open(pdf_file, "wb") as file:
        file.write(response.content)

    include_header = True

    output_rows = []
    with pdfplumber.open(pdf_file) as pdf:
        for idx, page in enumerate(pdf.pages):
            rows = page.extract_tables()[0]

            for row in rows:
                output_row = []
                for column in row:
                    if column is None:
                        output_row.append("")
                    else:
                        # Collapse newlines
                        partial = re.sub(r"\n", " ", column)
                        # Standardize whitespace
                        clean_text = re.sub(r"\s+", " ", partial)
                        output_row.append(clean_text)

                if len(output_row) > 0 and (
                    output_row[0] != "Date of Letter" or include_header
                ):
                    output_rows.append(output_row)

            include_header = False

    # Write out the data to a CSV
    data_path = data_dir / "id.csv"
    utils.write_rows_to_csv(output_rows, data_path)

    return data_path


if __name__ == "__main__":
    scrape()
