import csv
from os.path import join, expanduser
from pathlib import Path


def default_user_home():
    return join(
        expanduser('~'),
        '.warn-scraper'
    )


def write_rows_to_csv(rows, output_path, mode='w'):
    with open(output_path, mode, newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)
