import os
import logging
import requests
import xlrd
import pandas as pd

from bs4 import BeautifulSoup
from datetime import date

# spot-check once more

def scrape(output_dir):

    logger  = logging.getLogger(__name__)

    url = 'https://www.edd.ca.gov/jobs_and_training/warn/WARN_Report.xlsx'
    df = pd.read_excel(url)
    cali_data_today = os.environ['WARN_DATA_PATH']
    cali_data_path = '{}/california_warn_raw.csv'.format(cali_data_today)
    df.to_csv(cali_data_path)
    ca_data = pd.read_csv(cali_data_path)

    ca_data = ca_data.iloc[:,1:]
    ca_data.dropna(axis=0, how='all', inplace=True)

    ca_data = ca_data[1:]
    headers = ca_data.iloc[0]
    ca_data.columns = headers
    ca_data = ca_data[1:]
    ca_data.columns = ca_data.columns.str.replace('\\n',' ')

    ca_data = ca_data[['Notice Date', 'Effective Date', 'Received Date', 'Company', 'City', 'County', 'No. Of Employees ', 'Layoff/Closure Type']]
    ca_data = ca_data.dropna(subset=['Effective Date', 'Received Date', 'Company', 'County'])

    cali_hist_data = os.environ['PROCESS_DIR']
    cali_hist_path = '{}/california_warn_raw_start.csv'.format(cali_hist_data)
    cali_hist = pd.read_csv(cali_hist_path)

    ca_data.rename(columns={"No. Of Employees ": "Employees"}, inplace=True)
    ca_data.rename(columns={"Layoff/Closure Type": "Layoff/Closure"}, inplace=True)

    ca_data['Notice Date'] = pd.to_datetime(ca_data['Notice Date'])
    ca_data['Effective Date'] = pd.to_datetime(ca_data['Effective Date'])
    ca_data['Received Date'] = pd.to_datetime(ca_data['Received Date'])

    ca_data['Notice Date'] = ca_data['Notice Date'].dt.strftime('%m/%d/%Y')
    ca_data['Effective Date'] = ca_data['Effective Date'].dt.strftime('%m/%d/%Y')
    ca_data['Received Date'] = ca_data['Received Date'].dt.strftime('%m/%d/%Y')

    all_ca_data = pd.concat([ca_data, cali_hist])
    all_ca_data.drop_duplicates(inplace=True)

    output_file = '{}/california_warn_raw.csv'.format(output_dir)
    all_ca_data.to_csv(output_file, index=False)


if __name__ == '__main__':
    scrape()