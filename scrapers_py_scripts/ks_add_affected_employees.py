from os import path
import os

import csv 
from datetime import datetime
import pandas as pd

from bs4 import BeautifulSoup
import requests

def add_affected_ks():

    ks_data = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/kansas_warn_raw.csv')
    base_url = 'https://www.kansasworks.com/ada/'

    full_url_list = []
    for url_suffix in ks_data['url_suffix']:
        full_url = base_url + url_suffix
        full_url_list.append(full_url)

    employees_affected = [['URL','Affected Employees']]
    short_list = full_url_list[39:42]
    for url in full_url_list:
        print(url)
        # print('1')
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find('table') # output is list-type
    #     print(table)
        rows = table.find_all('tr')
        for row in rows:
            if 'employees' in row.text:
                data = row.find_all('td')
                affected_num = data[1].get_text()
                affected_num = affected_num.replace(u'\xa0', u'')
                if 'Company' in affected_num:
    #                 print('doing nothing')
                    company = 'doing nothing'
                else:
                    keep_data = [url, affected_num]
                    employees_affected.append(keep_data)
# https://www.kansasworks.com/ada/
    # print(employees_affected)
    headers = employees_affected.pop(0)
    df = pd.DataFrame(employees_affected, columns=headers)
    df['Suffix'] = df['URL'].str.split('/ada/').str[-1]
    print(df)
   

    df = df.drop_duplicates(subset='URL', keep="first")
    # pd.options.display.max_rows = 999
    # print(df)
    # print(ks_data)
    # # print(' ')
    # # print(' ')
    all_ks_data = pd.merge(ks_data, df, left_on='url_suffix', right_on='Suffix')
    # print(all_ks_data)
    all_ks_data.drop(columns=['Unnamed: 0','Suffix', 'url_suffix'], inplace=True)
    # print(ks_data)
    # print(' ')
    # print(' ')

    # print(all_ks_data)

    all_ks_data.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/kansas_warn_raw.csv')



if __name__ == '__main__':
    add_affected_ks()