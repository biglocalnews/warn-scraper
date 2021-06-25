import pandas as pd


def scrape(output_dir, cache_dir=None):
    url = 'https://wsd.dli.mt.gov/_docs/wioa/warn.xlsx'
    df = pd.read_excel(url)
    output_file = '{}/montana_warn_raw.csv'.format(output_dir)
    df.to_csv(output_file, index=False)
    return output_file
