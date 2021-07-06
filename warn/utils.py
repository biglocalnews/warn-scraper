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


def write_dict_rows_to_csv(path, headers, rows, mode='w'):
    with open(path, mode, newline='') as out:
        writer = csv.DictWriter(out, fieldnames=headers)
        if mode == 'w':
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
