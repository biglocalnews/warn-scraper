#!/usr/bin/env python

import gzip
import re
import os
import requests
import subprocess

from bs4 import BeautifulSoup
from os import path
from datetime import datetime
import pandas as pd

def newyork():

    subprocess.call([
        'curl',
        '-o',
        '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/warn_2020.html',
        'https://labor.ny.gov/app/warn/default.asp?warnYr=2020'
    ])


    with open('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/warn_2020.html', 'r', errors='ignore') as html:
        response = html.read()

    soup = BeautifulSoup(response, 'html.parser')
    table = soup.table
    link_tags = table.find_all('a')

    links = []
    titles = []
    warn_url = "https://labor.ny.gov/app/warn/"

    # Iterate over each <a>
    for link in table.find_all('a'):
        title = link.text
        full_link = warn_url + link['href']
        links.append(full_link)
        titles.append(title)

    already_downloaded = []

    for i in os.listdir('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/2020_files'):
        if i == '.DS_Store':
            continue
        elif i == 'titles.csv':
            continue
        elif i == '.ipynb_checkpoints':
            continue
        else:
            file = i.split('warn_ny_')[1]
            file = file.split('_2020.html')[0]
            url = 'https://labor.ny.gov/app/warn/details.asp?id='
            full_url = url + file
            already_downloaded.append(full_url)

    missing_links = list(set(links) - set(already_downloaded))

    missing_titles = []
    counter = 0
    for i in links:
        counter += 1
        missed = titles[counter - 1]
        if i in missing_links:
            missed_dict = {'url':i, 'title':missed}
            missing_titles.append(missed_dict)

    # Import the time library to let us wait in between each request
    import time

    # gzip allows us to unzip improperly zipped files
    import gzip

    from tqdm import tqdm

    def get_page(url):

        response = requests.get(url)

        # This is pretty atypical. Some of these pages are not being unzipped correctly
        # If the request didn't automatically unzip the html, we have to do it ourselves
        # We can check the encoding that the requests library thinks the page has returned
        if response.apparent_encoding is None:
            try:
                html = gzip.decompress(response.content).decode('utf-8')
                
            except UnicodeDecodeError:

                print(url)
                html = gzip.decompress(response.content).decode('utf-8', errors='ignore')


        else:
            html = response.text

        # Remove non-breaking space characters in the HTML
        html = html.replace('&nbsp;', ' ')

        return html


    # Create a list of HTML pages
    year = 2020
    # warn_pages = []
    links_short = links[0:4]
    for link in tqdm(missing_links):
        html = get_page(link)
        last = link.split('=')[1]
    #     print(last)
        open(f'/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/2020_files/warn_ny_{last}_{year}.html', 'w').write(html)
    #     warn_pages.append(html)

        time.sleep(1)
        
    print('done fetching data')


    file_path = os.listdir('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/2020_files')
    actual_path = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/2020_files'
    warn_url = 'https://labor.ny.gov/app/warn/details.asp?id='


    missing_pages = []
    for i in missing_links:
        file = i.split('=')[1]
        html = f'warn_ny_{file}_2020.html'
        full_page = f'{actual_path}/{html}'
        missing_pages.append(full_page)


    import re

    def parse_warn_page(html, url):

        # Create a dictionary to store the data for a single WARN listing
        page_data = {'URL': url}
        #  print(page_data)

        # Make the soup for the single page
        page_soup = BeautifulSoup(html, 'html.parser')

        # Sanity check
        # print(page_soup.prettify())

        # Get the first table (there should only be one)
        
        table = page_soup.table

        # Get all text in the table
        # get_text() will get all text in all elements underneath the current element, 
        # in this case all of the text in the <p> tags
        table_text = table.get_text()

        # Split the text into a list of lines based on the newline character '\n'
        lines = table_text.split('\n')
        missing_data = []
        keys = []

        # Iterate over each line
        counter = 0

        for i, line in enumerate(lines):
            counter += 1
            line = line.strip()
            line = line.replace('  ', ' ')
            line = line.replace('Dates', 'Date')
            line = line.replace('Counties', 'County')
            line = line.replace('Contact(s)', 'Contact')
            line = line.replace('Rapid Response Specialist ', 'Rapid Response Specialist') # add all the changes from DF replace columns & then run again
            line = line.replace('Rapid Response Specialists', 'Rapid Response Specialist') # for all years 2015-2020
            line = line.replace('Unions', 'Union')
            line = line.replace('ERNUM', 'FEIN NUM')
            line = line.replace('Control Number', ' Event Number')
            line = line.replace('Event Number', ' Event Number')
            line = line.replace('  Event Number', ' Event Number')
            line = line.replace('WIB Name', 'WDB Name')
            line = line.replace(' WDB Name', 'WDB Name')
            line = line.replace(' WBD Name', 'WDB Name')
            line = line.replace('WBD Name', 'WDB Name')
            line = line.replace('Total Employees ', 'Total Employees:')
            line = line.replace('Business Type ', 'Business Type:')
            line = line.replace('W DB Name', 'WDB Name')
            line = line.replace('Company ', 'Company:')
            split_text = line.split(':', 1)
    #         print(line)
            
            if len(split_text) == 2:
                key = split_text[0]
                value = split_text[1]
                page_data[key] = value
                if value == '':
                    missing_data.append(key)

                # The County data is formatted weirdly, using | to delimit some columns we want in our data
                try:
                    if key == 'County':
                        
                        split_row = value.split('|')
                        page_data['County'] = split_row[0]
                        for loc_data in split_row[1:]:
    #                         print(loc_data)
                            split_loc_data = loc_data.split(':')
                            
                            #these lines below fixed it
                            if len(split_loc_data) > 1:
                                key = split_loc_data[0]
                                value = split_loc_data[1]
                                page_data[key] = value
                            
                except IndexError:
                    print("*****************************************************")

        
            if len(split_text) < 2:
                missing_data.append(line)
        try:
            missing_data = list(filter(None, missing_data))
            new_key = missing_data[0]
            missing_data = missing_data[1:]
    
            value = ' '.join(map(str, missing_data))
    #         print(value)
            page_data[new_key] = value
        except IndexError:
            a = 'a'
                    
        return page_data


    # # Create a list to store the data we scrape.
    # # Each item in the list will correspond to a single WARN listing
    # # Each column will be a piece of single labeled piece information from the listing
    data = []

    """ Comment out loop below when testing individual links"""

    file_path_short = file_path[0:2]
    page_data = []
    for html_page in missing_pages:
        file = html_page.split('warn_ny_')[1]
        file = file.split('_2020.html')[0]
        url = 'https://labor.ny.gov/app/warn/details.asp?id='
        full_url = url + file
        resp = open(html_page, 'r', encoding="utf-8", errors='ignore')
        try:
            page_data = parse_warn_page(resp, full_url)
            data.append(page_data)
        except AttributeError:
            print(url)   

    df = pd.DataFrame(data)
    df2 = pd.DataFrame.from_dict(missing_titles)

    df = df[['URL', 'Date of Notice', ' Event Number', 'Rapid Response Specialist',
        'Reason Stated for Filing', 'Company', 'County', 'WDB Name', ' Region',
        'Contact', 'Phone', 'Business Type', 'Number Affected',
        'Total Employees', 'Layoff Date', 'Closing Date',
        'Reason for Dislocation', 'FEIN NUM', 'Union', 'Classification']]


    df_and_titles = pd.merge(df, df2, left_on='URL', right_on='url')
    df_and_titles.rename(columns={'title':'notice_title'}, inplace=True)
    final_df = df_and_titles[['notice_title','URL', 'Date of Notice', ' Event Number', 'Rapid Response Specialist',
        'Reason Stated for Filing', 'Company', 'County', 'WDB Name', ' Region',
        'Contact', 'Phone', 'Business Type', 'Number Affected',
        'Total Employees', 'Layoff Date', 'Closing Date',
        'Reason for Dislocation', 'FEIN NUM', 'Union', 'Classification']]


    final_df['New Notice'] = final_df['Date of Notice'].str.strip(' ')
    final_df['Amended'] = final_df['New Notice'].str.split(' ', 1)
    final_df['Amended'] = final_df['Amended'].apply(lambda x: x[1] if len(x) > 1 else '')
    final_df.drop(columns='New Notice', inplace = True)

    recent = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/newyork_warn_recent.csv')

    final = pd.concat([final_df, recent])
    final = final.loc[:, ~final.columns.str.startswith('Unnamed')]
    final.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/newyork_warn_raw.csv')
    final.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/newyork_warn_recent.csv')


if __name__ == '__main__':
    newyork()


