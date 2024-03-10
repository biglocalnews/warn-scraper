import os
import re
from pathlib import Path

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs, Ash1R"]
__tags__ = ["html"]
__source__ = {
    "name": "Pennsylvania Department of Labor & Industry",
    "url": "https://www.dli.pa.gov/Individuals/Workforce-Development/warn/notices/Pages/default.aspx",
}


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Pennsylvania.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)
    Returns: the Path where the file is written
    """
    state_code = "pa"
    cache = Cache(cache_dir)

    # The basic configuration for the scrape
    base_url = "https://www.dli.pa.gov"

    url = (
        f"{base_url}/Individuals/Workforce-Development/warn/notices/Pages/default.aspx"
    )
    response = utils.get_url(url)
    document = BeautifulSoup(response.text, "html.parser")
    links = document.find("table").find_all("a")

    output_rows = []

    for link in links:
        url = f"{base_url}{link.get('href')}"
        cache_key = f"{state_code}/{os.path.basename(url).replace('.aspx', '')}.html"

        utils.fetch_if_not_cached(cache.path / cache_key, url)
        html = cache.read(cache_key)
        cache.write(cache_key, html)

        # Scrape out the table
        new_rows = _parse_table(html)

        # Concatenate the rows
        output_rows.extend(new_rows)

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"

    utils.write_dict_rows_to_csv(
        data_path,
        [
            "COMPANY",
            "LOCATION",
            "COUNTY",
            "# AFFECTED",
            "EFFECTIVE DATE",
            "CLOSURE OR LAYOFF",
        ],
        output_rows,
    )

    # Return the path to the CSV
    return data_path


def _parse_table(html, include_headers=True):
    """
    Parse HTML table.

    Keyword arguments:
    html -- the HTML to parse
    include_headers -- whether to include the headers in the output (default True)
    Returns: a list of rows
    """
    # Parse out data table
    document = BeautifulSoup(html, "html.parser")
    cells = document.find_all("table")[0].find_all("td")

    output_rows = []

    for cell in cells:
        row = {}
        seen_fields = False

        cell_html = str(cell)
        lines = re.split(r"\<[\/]{0,1}(?:div|br|p)[^\>]*\>|\n", cell_html)

        name = None
        for line in lines:
            clean_text = _clean_text(
                re.sub(r"\<[^>]*\>|\xa0", " ", line).replace("&amp;", "&")
            )
            is_bolded = bool(re.search(r"\<\/?strong|b\>", line))
            is_field = bool(
                re.search(r"\:.+|# AFFECTED\:|EFFECTIVE DATE\:", clean_text)
            )
            is_type = bool(
                re.search(
                    r"LAYOFF|CLOSING|CLOSURE|PERMANENT|CONTRACT CANCELLED|REDUCTION OF FORCE",
                    clean_text,
                    re.I,
                )
            )
            is_empty = len(clean_text) == 0

            if bool(
                re.search(
                    r"^([1-9A-Z]+ PHASE|PHASE [1-9]|ENDING|1ST|2ND|3RD|[1-9]+TH)\:",
                    clean_text,
                    re.I,
                )
            ):
                name = "EFFECTIVE DATE"
                value = clean_text
            elif is_field:
                seen_fields = True
                parts = clean_text.split(":", 1)
                name = parts[0].upper()

                if "DATE" in name:
                    name = "EFFECTIVE DATE"
                elif "LAYOFF" in name:
                    name = "CLOSURE OR LAYOFF"
                elif "AFFECTED" in name:
                    name = "# AFFECTED"
                elif "COUNTIES" in name:
                    name = "COUNTY"
                elif "MULTIPLE STATE EMPLOYER" in name:
                    name = None
                    continue
                elif "LOCATION" in name:
                    name = "LOCATION"

                value = parts[1].strip()
            elif is_bolded and is_type and seen_fields:
                name = "CLOSURE OR LAYOFF"
                value = clean_text
            elif is_bolded:
                if seen_fields:
                    output_rows.append(row)
                    row = {}
                    seen_fields = False
                name = "COMPANY"
                value = clean_text
            elif not is_empty:
                name = "LOCATION"
                value = clean_text
            else:
                name = None
                value = None

            if name and value:
                if name not in row:
                    row[name] = value
                else:
                    row[name] += f" {value}"

        if len(row.values()) > 0:
            output_rows.append(row)

    return output_rows


def _clean_text(text):
    if text is None:
        return ""
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


if __name__ == "__main__":
    scrape()
