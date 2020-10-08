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
    # output_csv = '{}/california_warn_raw.csv'.format(output_dir)
    cali_data_today = os.environ['CALI_CURRENT_DATA']
    cali_data_path = '{}/california_warn_raw.csv'.format(cali_data_today)
    df.to_csv(cali_data_path, index = None)
    ca_data = pd.read_csv(cali_data_path)
    ca_data = ca_data.iloc[2:-16]

    headers = ca_data.iloc[0]
    ca_data = ca_data[1:]
    ca_data.columns = headers

    ca_data = ca_data[['Notice Date', 'Effective Date', 'Received Date', 'Company', 'City', 'County', 'No. Of Employees ', 'Layoff/Closure']]
    ca_data = ca_data[:-1]

    cali_hist_data = os.environ['CALI_HIST_DATA']
    cali_hist_path = '{}/california_warn_raw_start.csv'.format(cali_hist_data)

    recent = pd.read_csv(cali_hist_path)
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
    output_file = '{}/california_warn_raw.csv'.format(output_dir)
    all_ca_data.to_csv(output_file, index=False)


if __name__ == '__main__':
    scrape()