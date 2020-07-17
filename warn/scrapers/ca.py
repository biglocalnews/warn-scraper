import requests
import xlrd
import pandas as pd

from bs4 import BeautifulSoup
from datetime import date

# spot-check once more

def scrape():

    url = 'https://www.edd.ca.gov/jobs_and_training/warn/WARN_Report.xlsx'
    df = pd.read_excel(url)
    df.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/california_warn_raw.csv', index = None)
    ca_data = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/california_warn_raw.csv')
    ca_data = ca_data.iloc[2:-16]

    headers = ca_data.iloc[0]
    ca_data = ca_data[1:]
    ca_data.columns = headers

    ca_data = ca_data[['Notice Date', 'Effective Date', 'Received Date', 'Company', 'City', 'County', 'No. Of Employees ', 'Layoff/Closure']]
    ca_data = ca_data[:-1]
    recent = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/california_warn_raw_start.csv')
    recent = recent.loc[:, ~recent.columns.str.startswith('Unnamed')]

    ca_data = ca_data.rename(columns={'Notice Date':'Notice_Date', 'Effective Date':'Effective_Date', 'Received Date': 'Received_Date', 'No. Of Employees ': 'No_employees'})

    ca_data['Notice_Date'] = pd.to_datetime(ca_data['Notice_Date'])
    ca_data['Effective_Date'] = pd.to_datetime(ca_data['Effective_Date'])
    ca_data['Received_Date'] = pd.to_datetime(ca_data['Received_Date'])

    ca_data['Notice_Date'] = ca_data['Notice_Date'].dt.strftime('%m/%d/%Y')
    ca_data['Effective_Date'] = ca_data['Effective_Date'].dt.strftime('%m/%d/%Y')
    ca_data['Received_Date'] = ca_data['Received_Date'].dt.strftime('%m/%d/%Y')

    all_ca_data = pd.concat([ca_data, recent])
    all_ca_data.drop_duplicates(inplace=True)
    all_ca_data.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/california_warn_raw.csv', index=False)


if __name__ == '__main__':
    scrape()