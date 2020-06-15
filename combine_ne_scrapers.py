import os
import pathlib

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json


def combine():
    files_to_concat = [
        'nebraska_warn_raw1.csv',
        'nebraska_warn_raw2.csv'
    ]
    merged_file = os.path.join('data', 'nebraska_warn_raw.csv')
    with open(merged_file, 'w') as outfile:
        for source_file in files_to_concat:
            with open(os.path.join('data', source_file), 'r') as infile:
                for row in infile:
                    #TODO: Add filter to pluck out the header row
                    # in second file;
                    # TODO: Align the files into a standard data structure?
                    outfile.write(row)


if __name__ == '__main__':
    combine()
