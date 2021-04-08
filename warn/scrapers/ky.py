import os
import logging
import requests
import xlrd
import openpyxl
import pandas as pd

def scrape(output_dir):

    logger  = logging.getLogger(__name__)
    url = 'https://kcc.ky.gov/WARN%20notices/WARN%20Notices%202021/WARN%20Notice%20Report%2003222021%20.xlsx'

    df = pd.read_excel(url, sheet_name = None)
    empty_df = pd.DataFrame()

    for sheet in df:
        indiv_sheet = pd.read_excel(url, sheet_name = sheet)
        indiv_sheet['Year'] = sheet
        
        if 'Unnamed: 11' in indiv_sheet.columns:
            indiv_sheet.drop(columns='Unnamed: 11', inplace=True)
        if 'County: County Name' in indiv_sheet.columns:
            indiv_sheet.rename(columns={'County: County Name': 'County'}, inplace=True)
        empty_df = pd.concat([empty_df, indiv_sheet])

    output_file = '{}/kentucky_warn_raw.csv'.format(output_dir)
    empty_df.to_csv(output_file, index=False)


if __name__ == '__main__':
    scrape()