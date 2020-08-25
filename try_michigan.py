import csv
import logging
import re
import requests

from bs4 import BeautifulSoup
from bs4 import NavigableString

url = 'https://milmi.org/warn'
page = requests.get(url)

soup = BeautifulSoup(page.text, 'html5lib')
table = soup.table

headers = [
            'Company Name',
            'City',
            'Date Received',
            'Incident Type',
            'Number of Layoffs'
            ]

table_row_list = []
table_rows = table.find_all('tr')

for tr in table_rows:
    table_data = tr.find_all('td')
    table_data_list = []
    for td in table_data:
        table_data_list.append(td.text)
    table_row_list.append(table_data_list)

table_row_list = table_row_list[1:]
for row in table_row_list:
    counter = 0
    for i in row:
        i = i.replace('\t', '')
        i = i.replace('\n', '')

        row[counter] = i
        counter += 1


url_2 = 'https://milmi.org/warn/archive#warn2019'
page_2 = requests.get(url_2)
soup_2 = BeautifulSoup(page_2.text, 'html5lib')

table_row_list_next = []
tables = soup_2.find_all('table')
print(len(tables))

for table in tables:
    table_row_list_2 = []
    table_rows = table.find_all('tr')

    for tr in table_rows:
        table_data = tr.find_all('td')
        table_data_list_2 = []
        for td in table_data:
            table_data_list_2.append(td.text)
        table_row_list_2.append(table_data_list_2)
    table_row_list_next.extend(table_row_list_2)


table_row_list_next = table_row_list_next[1:]
for row in table_row_list_next:
    counter = 0
    for i in row:
        i = i.replace('\t', '')
        i = i.replace('\n', '')

        row[counter] = i
        counter += 1


table_row_list.extend(table_row_list_next)
# print(table_row_list)

with open('try_michigan.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)

with open('try_michigan.csv', 'a') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(table_row_list)

        

