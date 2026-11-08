import logging
import re
from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html"]
__source__ = {
    "name": "Maryland Department of Labor",
    "url": "https://www.dllr.state.md.us/employment/warn.shtml",
}

logger = logging.getLogger(__name__)

naptime = 3

# Maryland has changed its table layout over the years. Pages from 2023 on have "Local Area" and
# "Type" columns holding names; 2022 and earlier have "WIA Code" and "Type Code" columns holding
# numbers, with the key printed on the page. Each page is read against its own header and mapped
# into these columns. For code-style pages the number stays in its own column, and the name from
# that page's own key goes into "Local Area" or "Type".
OUTPUT_COLUMNS = [
    "Notice Date",
    "NAICS Code",
    "Company",
    "Location",
    "Local Area",
    "Total Employees",
    "Effective Date",
    "Type",
    "WIA Code",
    "Type Code",
]


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Maryland.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # In November 2024 Maryland began throwing out many failed connection messages. These two things helped.
    request_headers = {"User-Agent": "BigLocalNews.org"}
    request_verify = False

    # Get the page
    url = "https://www.dllr.state.md.us/employment/warn.shtml"
    r = utils.get_url(url, headers=request_headers, verify=request_verify)
    r.encoding = "utf-8"
    html = r.text

    # Save it to the cache
    cache.write("md/source.html", html)

    sleep(naptime)  # Try to stop blocked connections by being less aggressive

    # Parse the list of links
    soup = BeautifulSoup(html, "html.parser")
    a_list = soup.find_all("a", {"class": "sub"})
    href_list = [a["href"] for a in a_list]

    # Download them all
    html_list = []
    html_list.append(html)  # Save the source HTML for parsing also

    old_pages = [
        "warn2025.shtml",
        "warn2024.shtml",
        "warn2023.shtml",
        "warn2022.shtml",
        "warn2021.shtml",
        "warn2020.shtml",
        "warn2019.shtml",
        "warn2018.shtml",
        "warn2017.shtml",
        "warn2016.shtml",
        "warn2015.shtml",
        "warn2014.shtml",
        "warn2013.shtml",
        "warn2012.shtml",
        "warn2011.shtml",
        "warn2010.shtml",
    ]

    for href in href_list:
        # Request the HTML
        url = f"https://www.dllr.state.md.us/employment/{href}"
        filename = f"md/{href}.html"

        if href not in old_pages:
            logger.debug(f"Trying special handling on {href}")
            sleep(naptime)  # Try to stop blocked connections by being less aggressive
            r = utils.get_url(url, headers=request_headers, verify=request_verify)
            r.encoding = "utf-8"
            html = r.text

            # Save it to the cache
            cache.write(filename, html)
        else:
            r = utils.fetch_if_not_cached(
                cache_dir / filename,
                url,
                headers=request_headers,
                verify=request_verify,
            )
            html = cache.read(filename)

        # Add it to the list
        html_list.append(html)

    # Parse them all, each page against its own header
    output_rows = [OUTPUT_COLUMNS]
    for html in html_list:
        output_rows.extend(parse_page(html))

    # Set the export path
    data_path = data_dir / "md.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


def parse_page(html: str) -> list:
    """Parse one Maryland WARN page into rows ordered like OUTPUT_COLUMNS (no header row).

    The page's first table is read with the page's own header row. An unrecognized column name, or a
    row with a different number of cells than the header, raises instead of producing misaligned data.
    """
    soup = BeautifulSoup(html, "html5lib")
    table_list = soup.find_all("table")
    assert len(table_list) > 0
    row_list = table_list[0].find_all("tr")

    def cells(row):
        return [_clean_text(c.text) for c in (row.find_all("td") or row.find_all("th"))]

    by_lower = {c.lower(): c for c in OUTPUT_COLUMNS}
    header = cells(row_list[0])
    unknown = [h for h in header if h.lower() not in by_lower]
    if unknown:
        raise ValueError(
            f"Unrecognized Maryland WARN column(s) {unknown}; the page layout has changed"
        )
    header = [by_lower[h.lower()] for h in header]
    legends = _read_legends(html)

    rows = []
    for row in row_list[1:]:
        values = cells(row)
        if not values:
            continue
        if len(values) != len(header):
            raise ValueError(
                f"Maryland WARN row has {len(values)} cells but the header has {len(header)}: {values}"
            )
        record = dict(zip(header, values))
        if record.get("WIA Code") and not record.get("Local Area"):
            record["Local Area"] = _decode_area(
                record["WIA Code"], legends["Local Area"]
            )
        if record.get("Type Code") and not record.get("Type"):
            record["Type"] = _decode_type(record["Type Code"], legends["Type"])
        rows.append([record.get(c, "") for c in OUTPUT_COLUMNS])
    return rows


def _decode_area(raw: str, legend: dict) -> str:
    """Names for a "WIA Code" cell like "7", "7,8" or "7 & 8". Anything else ("Various", "N/A") returns "";
    the raw text stays in the WIA Code column."""
    if not re.fullmatch(r"\s*\d+(\s*[,&]\s*\d+)*\s*", raw):
        return ""
    names = [legend.get(code, "") for code in re.findall(r"\d+", raw)]
    if not all(names):
        logger.debug(f"WIA Code {raw!r} has a code that is not in the page's key")
        return ""
    return " / ".join(names)


def _decode_type(raw: str, legend: dict) -> str:
    """Name for a "Type Code" cell like "2" or "2 (Possibly turning into a closure)", keeping the note.
    Anything that doesn't start with a code in the page's key returns ""; the raw text stays in Type Code.
    """
    match = re.match(r"\s*(\d+)\b\s*(.*)$", raw)
    if not match or match.group(1) not in legend:
        return ""
    return f"{legend[match.group(1)]} {match.group(2)}".strip()


def _read_legends(html: str) -> dict:
    """Read the "Local Area Codes" and "Type Codes" keys printed outside the table on older pages."""
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        table.decompose()
    text = _clean_text(soup.get_text(" "))

    def read(pattern):
        match = re.search(pattern, text)
        if not match:
            return {}
        return dict(re.findall(r"(\d+)\.\s+(.*?)(?=\s+\d+\.\s|$)", match.group(1)))

    return {
        "Local Area": read(r"Local Area Codes\s+(.*?)\s+Type Codes"),
        "Type": read(r"Type Codes\s+(.*?)(?:\s+Download|\s+Work Adjustment|$)"),
    }


def _clean_text(text):
    """Clean up the provided HTML snippet."""
    if text is None:
        return ""
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


if __name__ == "__main__":
    scrape()
