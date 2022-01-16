import re
import shutil
import typing
import logging
from pathlib import Path

import requests
import pdfplumber
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from .. import utils
from ..cache import Cache


logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from California.

    Compiles a single CSV for CA using historical PDFs and an Excel file for the current fiscal year.

    Only regenerates the CSV if a PDF or the Excel file have changed.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "ca.csv"
    # Set up cache dir for state
    cache_state = Path(cache_dir, "ca")
    cache_state.mkdir(parents=True, exist_ok=True)
    # Initially write to a temp file in cache_dir before
    # over-writing prior output_csv, so we can use append
    # mode while avoiding data corruption if script errors out
    temp_csv = "{}/ca_temp.csv".format(cache_state)
    # Create Cache instance for downstream operations
    cache = Cache(cache_dir)
    # Update pdfs and Excel files
    files_have_changed = _update_files(cache)
    output_headers = [
        "notice_date",
        "effective_date",
        "received_date",
        "company",
        "city",
        "num_employees",
        "layoff_or_closure",
        "county",
        "address",
        "source_file",
    ]
    if files_have_changed:
        logger.info("One or more source data files have changed")
        logger.info("Extracting Excel data for current fiscal year")
        wb_path = cache.files(subdir="ca", glob_pattern="*.xlsx")[0]
        excel_data = _extract_excel_data(wb_path)
        # Write mode when processing Excel
        utils.write_dict_rows_to_csv(
            temp_csv, output_headers, excel_data, mode="w", extrasaction="ignore"
        )
        logger.info("Extracting PDF data for prior years")
        for pdf in cache.files(subdir="ca", glob_pattern="*.pdf"):
            logger.info(f"Extracting data from {pdf}")
            data = _extract_pdf_data(pdf)
            # Append mode when processing PDFs
            utils.write_dict_rows_to_csv(
                temp_csv, output_headers, data, mode="a", extrasaction="ignore"
            )
        # If all went well, copy temp csv over pre-existing output csv
        shutil.copy2(temp_csv, output_csv)
    return output_csv


def _update_files(cache):
    files_have_changed = False
    # Create lookup of pre-existing PDF files and their size
    files = {}
    for local_file in cache.files(subdir="ca/"):
        fname = local_file.split("/")[-1]
        extension = fname.split(".")[-1]
        if extension in ["pdf", "xlsx"]:
            files[fname] = Path(local_file).stat().st_size
    # Download file if it has changed or not present.
    links = _get_file_links()
    for link in links:
        file_name = link["url"].split("/")[-1]
        target_path = Path(cache.path, f"ca/{file_name}")
        download_status = False
        # If file doesn't exist, update download status
        try:
            local_size = files[file_name]
        except KeyError:
            download_status = True
            local_size = None
        # If size doesn't match, update download status
        if local_size != link["size"]:
            download_status = True
        if download_status is True:
            files_have_changed = True
            logger.info(f"Downloading {file_name} to {target_path}")
            utils.download_file(link["url"], target_path)
    # Delete local files whose names don't match
    # data files on remote site, in order to guard against
    # duplicates if the source agency renames files
    for obsolete_file in _obsolete_local_files(files, links):
        files_have_changed = True
        logger.info(
            f"Deleting local file no longer present on source site: {obsolete_file}"
        )
        Path(cache.path, f"ca/{obsolete_file}").unlink()
    return files_have_changed


def _get_file_links():
    """Get links to historical PDFs and the Excel file."""
    logger.info("Getting metadata for data files")
    base_url = "https://edd.ca.gov/Jobs_and_Training"
    home_page = f"{base_url}/Layoff_Services_WARN.htm"
    html = utils.get_url(home_page).text
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.find_all("a"):
        relative_file_url = link.attrs.get("href", "")
        if _is_warn_report_link(relative_file_url):
            file_url = f"{base_url}/{relative_file_url}"
            meta = _get_file_metadata(file_url)
            links.append(meta)
    return links


def _is_warn_report_link(url):
    return True if re.search(r"warn[-_]?report", url, re.I) else False


def _get_file_metadata(url):
    return {"url": url, "size": int(requests.head(url).headers["Content-Length"])}


def _extract_excel_data(wb_path):
    wb = load_workbook(filename=wb_path)
    # Get the only worksheet
    ws = wb.worksheets[0]
    rows = [row for row in ws.rows]
    # Throw away initial rows until we reach first data row
    while True:
        row = rows.pop(0)
        first_cell = row[0].value.strip().lower()
        if first_cell.startswith("county"):
            break
    payload = []
    for row in rows:
        first_cell = row[0].value.strip().lower()
        # Exit if we've reached summary row at bottom
        if first_cell == "report summary":
            break
        # Spreadsheet contains merged cells so index
        # positions below are not sequential
        data = {
            "county": row[0].value.strip(),
            "notice_date": _convert_date(row[1].value),
            "received_date": _convert_date(row[2].value),
            "effective_date": _convert_date(row[4].value),
            "company": row[5].value.strip(),
            "layoff_or_closure": row[8].value.strip(),
            "num_employees": row[10].value,
            "address": row[12].value.strip(),
            "source_file": wb_path.split("/")[-1],
        }
        payload.append(data)
    return payload


def _convert_date(dt):
    return dt.strftime("%m/%d/%Y")


def _extract_pdf_data(pdf_path):
    headers = [
        "notice_date",
        "effective_date",
        "received_date",
        "company",
        "city",
        "county",
        "num_employees",
        "layoff_or_closure",
        "source_file",
    ]
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            # All pages pages except last should have a single table
            # Last page has an extra summary table, but indexing
            # for the first should avoid grabbing the summary data
            rows = page.extract_tables()[0]
            # Remove header row on first page
            # and update the standardized "headers" var if the source
            # data has no county field, as in the case of
            # files covering 07/2016-to-06/2017 fiscal year and earlier
            if idx == 0:
                raw_header = rows.pop(0)
                raw_header_str = "-".join([col.strip().lower() for col in raw_header])
                if "county" not in raw_header_str:
                    headers.remove("county")
            # Skip if it's a summary table (this happens
            # when summary is only table on page, as in 7/2019-6/2020)
            first_cell = rows[0][0].strip().lower()
            if "summary" in first_cell:
                continue
            for row in rows:
                data_row = dict(zip(headers, row))
                # Data clean-ups
                data_row.update(
                    {
                        "effective_date": data_row["effective_date"].replace(" ", ""),
                        "received_date": data_row["received_date"].replace(" ", ""),
                        "source_file": pdf_path.split("/")[-1],
                    }
                )
                data.append(data_row)
    return data


def _obsolete_local_files(pdfs, links):
    pdfs_uniq = set(pdfs.keys())
    remote_files = {link["url"].split("/")[-1] for link in links}
    return pdfs_uniq - remote_files


if __name__ == "__main__":
    scrape()
