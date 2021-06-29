from pathlib import Path
import csv


def write_rows_to_csv(rows, output_path):
    with open(output_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)
