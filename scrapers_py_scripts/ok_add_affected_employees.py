from os import path
import os

import csv 
from datetime import datetime
import pandas as pd

from bs4 import BeautifulSoup
import requests

def add_affected_ok():

    ok_data = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/oklahoma_warn_raw.csv')

    base_url = 'https://okjobmatch.com/ada/'

    full_url_list = []
    for url_suffix in ok_data['url_suffix']:
        full_url = base_url + url_suffix
        full_url_list.append(full_url)

    employees_affected = [['URL','Affected Employees']]
    # short_list = full_url_list[39:42]
    for url in full_url_list:
        print(url)
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

    # print(employees_affected)
    headers = employees_affected.pop(0)
    df = pd.DataFrame(employees_affected, columns=headers)
    
    df['Suffix'] = df['URL'].str[27:]
  
    df = df.drop_duplicates(subset='URL', keep="first")
    all_ok_data = pd.merge(ok_data, df, left_on='url_suffix', right_on='Suffix')
    all_ok_data.drop(columns=['Unnamed: 0','Suffix', 'url_suffix'], inplace=True)

    all_ok_data.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/oklahoma_warn_raw.csv', index=False)
    
    
    
if __name__ == '__main__':
    add_affected_ok()