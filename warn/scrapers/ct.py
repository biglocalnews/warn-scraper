import csv
import logging
import requests
import pandas as pd

from bs4 import BeautifulSoup

url = 'https://www.ctdol.state.ct.us/progsupt/bussrvce/warnreports/warn2016.htm'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find_all('table', 'style15')

for table_row in table[0].find_all('tr'):
    table_cells = table_row.find_all('td')
    print(table_cells)
    print(' ')