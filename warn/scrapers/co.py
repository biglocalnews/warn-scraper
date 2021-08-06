import csv
import logging

from pathlib import Path
from warn.cache import Cache
from warn.utils import download_file
from warn.utils import write_dict_rows_to_csv


logger = logging.getLogger(__name__)

# one set of fields per year, in order as listed on the year's document
FIELDS = [['', '', '', 'company', 'industry', '', '', '', '', 'address', '', "warn date", '', 'layoffs', "temporary_layoffs", "furloughs", "", "", 'layoff date'],
          ['company', 'industry', 'layoffs', 'local area', 'warn date', 'layoff date', 'layoff reason', 'attachment', 'occupations', '', '', ''],
          ['company', 'layoffs', 'local area', 'warn date', 'layoff reason', 'occupations', 'layoff date'],
          ['company', 'layoffs', 'local area', 'warn date', 'layoff reason'],
          ['company', 'layoffs', 'local area', 'warn date', 'layoff reason'],
          ['company', 'layoffs', 'local area', 'warn date', 'layoff reason'],
          ['company', 'layoffs', 'local area', 'warn date', 'layoff reason']]
OUTPUT_HEADERS = ['company', 'industry', 'address', 'local area', 'warn date', 'layoffs', 'layoff date', 'layoff reason', 'attachment']

def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/co.csv'
    cache = Cache(cache_dir)  # ~/.warn-scraper/cache
    # urls from 2021 to 2015
    urls = [
        'https://docs.google.com/spreadsheets/d/1HO8Fnm_4xey3Ctt6mYIig61Zx5iNq6_j_dlIaJvBS6o/edit#gid=1509741939',
        'https://docs.google.com/spreadsheets/d/1Km1mSUnCGE3EtZQTnZEUwxbdDTOcDZmNx6bviTwl2jI/edit#gid=0',
        'https://docs.google.com/spreadsheets/d/1GZEh1FUcHFfovdKeagTHFiv_P-PVVx64Bk4Szc963Gs/edit#gid=0',
        'https://docs.google.com/spreadsheets/d/1AsxrFpcg5nDdlezayogQf03Fq0Bkt6c34plqbEFxljI/edit#gid=0',
        'https://docs.google.com/spreadsheets/d/19YAbx8HAC9mfDbAkxVxBwEl8YCPGHhE91QHJAGi7R98/edit#gid=0',
        'https://docs.google.com/spreadsheets/d/1M-jYA2cSbehhp1pbpcAa900PtjAgktCHbU556cSjzc4/edit#gid=0',
        'https://docs.google.com/spreadsheets/d/1dpKX0g31Fkv8Hs3k3cVCJ19ce4RANNlYSCwpEQA2nrI/edit#gid=0']
    # convert google sheet into direct link to csv for downloading
    urls = [url.replace('/edit#gid=', '/export?format=csv&gid=') for url in urls]
    cache_state = Path(cache_dir, 'co')
    cache_state.mkdir(parents=True, exist_ok=True)
    output_rows = []
    # scrape from most recent to oldest (2015)
    # TODO probably merge 2021 layoff fields into total layoffs
    for num, url in enumerate(urls):
        intermediate_csv_path = f'{cache_state}/{num}.csv'
        # TODO try to read from cache first
        file_path = download_file(url, intermediate_csv_path)
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows_to_add = []
            for row_idx, row in enumerate(reader):
                if row_idx == 0:
                    # we are actually hard-coding headers for each year,
                    # so this part is commented out.

                    # only download headers once
                    # if not HEADERS:
                    #     HEADERS = row
                    # else:
                    #     pass
                    pass
                else:
                    # if a header is erroneously placed in the middle of the file
                    # (this is the case with row 7 of 2017 data)
                    if row[0] == 'Company':
                        continue
                    if row:
                        rows_to_add.append(row)
        # Convert rows to dicts, using each year's hard-coded FIELDS
        rows_as_dicts = [dict(zip(FIELDS[num], row)) for row in rows_to_add]
        output_rows.extend(rows_as_dicts)
        logger.info(f"Successfully scraped url {url}")
    write_dict_rows_to_csv(output_csv, OUTPUT_HEADERS, output_rows, extrasaction='ignore')

    return output_csv
