from os import path
import os
import pathlib

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

root = pathlib.Path(__file__).parent.resolve()

def combine():
#     ne_one = root / 'data' / 'nebraska_warn_raw1.csv'
#     ne_two = root / 'data' / 'nebraska_warn_raw2.csv'
    gh_link = 'https://raw.githubusercontent.com/biglocalnews/WARN/master/data/maryland_warn_raw.csv'
    gh_link2 = 'https://github.com/biglocalnews/WARN/blob/master/data/nebraska_warn_raw2.csv'
    ne_one = pd.read_csv(gh_link)
#     ne_two = pd.read_csv(gh_link2)
    
    
#     ne_two = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/nebraska_warn_raw2.csv')
#     ne_one = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/nebraska_warn_raw1.csv')
#     ne_two = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/nebraska_warn_raw2.csv')

#     ne_all_data = pd.concat([ne_one, ne_two])
#     ne_all_data.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/nebraska_warn_raw.csv')
#     os.remove('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/nebraska_warn_raw1.csv')
#     os.remove('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/nebraska_warn_raw2.csv')


if __name__ == '__main__':
    combine()
