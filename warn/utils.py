import csv
from os.path import join, expanduser

import requests


def write_rows_to_csv(rows, output_path, mode="w"):
    with open(output_path, mode, newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)


def write_dict_rows_to_csv(path, headers, rows, mode="w", extrasaction="raise"):
    with open(path, mode, newline="") as out:
        writer = csv.DictWriter(out, fieldnames=headers, extrasaction=extrasaction)
        if mode == "w":
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def download_file(url, local_path=None):
    with requests.get(url, stream=True) as r:
        if r.encoding is None:
            r.encoding = "utf-8"
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path
