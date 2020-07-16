from os import path
import os

import csv 
from datetime import datetime
import pandas as pd

from bs4 import BeautifulSoup
import requests

def add_affected():

    az_data = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/arizona_warn_raw.csv')

    base_url = 'https://www.azjobconnection.gov/ada/'

    full_url_list = []
    for url_suffix in az_data['url_suffix']:
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
    # print(len(df))
    df['Suffix'] = df['URL'].str.strip('https://www.azjobconnection.gov/ada/')
    # print(df)
    df = df.drop_duplicates(subset='URL', keep="first")
    all_az_data = pd.merge(az_data, df, left_on='url_suffix', right_on='Suffix')
    all_az_data.drop(columns=['Unnamed: 0','Suffix', 'url_suffix'], inplace=True)

    all_az_data.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/arizona_warn_raw.csv')
    
    
    
if __name__ == '__main__':
    add_affected()




    
    