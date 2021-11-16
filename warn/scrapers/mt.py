import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrape(output_dir, cache_dir=None):
    url = 'https://wsd.dli.mt.gov/wioa/related-links/warn-notice-page'
    response = requests.get(url)
    data_file_name = extract_file_name(response.text)
    data_url = f'https://wsd.dli.mt.gov/_docs/wioa/{data_file_name}'
    df = pd.read_excel(data_url, engine="openpyxl")
    output_file = f'{output_dir}/mt.csv'
    df.to_csv(output_file, index=False)
    return output_file

def extract_file_name(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find(id='boardPage').find_all('a')
    # Below URL will look like: ="../../_docs/wioa/warn-9-1-21.xlsx"
    return [
        link.attrs['href'] for link in links
        if link.attrs.get('href','').endswith('xlsx')
    ][0].split('/')[-1]
