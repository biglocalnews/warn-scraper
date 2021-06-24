import os
import logging
import pandas as pd


logger  = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    url = 'https://www.edd.ca.gov/jobs_and_training/warn/WARN_Report.xlsx'
    df = pd.read_excel(url)
    cali_data_path = f'{output_dir}/california_warn_raw.csv'
    df.to_csv(cali_data_path)
    ca_data = pd.read_csv(cali_data_path)
    ca_data = ca_data.iloc[:,1:]
    ca_data.dropna(axis=0, how='all', inplace=True)
    ca_data = ca_data[1:]
    headers = ca_data.iloc[0]
    ca_data.columns = headers
    ca_data = ca_data[1:]
    ca_data.columns = ca_data.columns.str.replace('\\n',' ')
    try:
        ca_data = ca_data[['Notice Date', 'Effective Date', 'Received Date', 'Company', 'City', 'County', 'No. Of Employees ', 'Layoff/Closure']]
    except:
        ca_data = ca_data[['Notice Date', 'Effective Date', 'Received Date', 'Company', 'City', 'County', 'No. Of Employees ', 'Layoff/Closure Type']]
    ca_data = ca_data.dropna(subset=['Effective Date', 'Received Date', 'Company', 'County'])
    ca_data.rename(columns={"No. Of Employees ": "Employees"}, inplace=True)
    try:
        ca_data.rename(columns={"Layoff/Closure Type": "Layoff/Closure"}, inplace=True)
    except:
         logger.error('There is no Layoff/Closure Type column to rename')
    ca_data['Notice Date'] = pd.to_datetime(ca_data['Notice Date'])
    ca_data['Effective Date'] = pd.to_datetime(ca_data['Effective Date'])
    ca_data['Received Date'] = pd.to_datetime(ca_data['Received Date'])
    ca_data['Notice Date'] = ca_data['Notice Date'].dt.strftime('%m/%d/%Y')
    ca_data['Effective Date'] = ca_data['Effective Date'].dt.strftime('%m/%d/%Y')
    ca_data['Received Date'] = ca_data['Received Date'].dt.strftime('%m/%d/%Y')
    cali_hist_path = f'{cache_dir}/california_warn_raw_start.csv'
    cali_hist = pd.read_csv(cali_hist_path)
    all_ca_data = pd.concat([ca_data, cali_hist])
    all_ca_data.drop_duplicates(inplace=True)
    output_file = f'{output_dir}/california_warn_processed.csv'
    all_ca_data.to_csv(output_file, index=False)
    return output_file

