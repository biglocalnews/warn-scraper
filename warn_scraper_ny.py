import requests
from bs4 import BeautifulSoup
import gzip
import re

from os import path

import csv 
from datetime import datetime

from bs4 import NavigableString
import os
import requests
import json
import pandas as pd
import re

def newyork():

    warn_url = "https://labor.ny.gov/app/warn/"
    warn_2020_url = "https://labor.ny.gov/app/warn/default.asp?warnYr=2020"
    response = requests.get(warn_2020_url)

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.table
    link_tags = table.find_all('a')

    links = []
    titles = []

    # Iterate over each <a>
    for link in table.find_all('a'):

    #     print('   ')
        title = link.text
        
        full_link = warn_url + link['href']
        links.append(full_link)
        titles.append(title)

    # Import the time library to let us wait in between each request
    import time
    # gzip allows us to unzip improperly zipped files
    import gzip

    from tqdm import tqdm

    def get_page(url):
        list = []
        # Fetch the page
        if url in list:
            print('url skipped')
        else:
            response = requests.get(url)
        #     print(url)


            # This is pretty atypical. Some of these pages are not being unzipped correctly
            # If the request didn't automatically unzip the html, we have to do it ourselves
            # We can check the encoding that the requests library thinks the page has returned
            if response.apparent_encoding is None:
                try:
                    html = gzip.decompress(response.content).decode('utf-8')
                except UnicodeDecodeError:
        #             print(counter)
                    print(url)
                    html = gzip.decompress(response.content).decode('utf-8', errors='ignore')
        #             print(url)
        #             continue

            else:
                html = response.text

            # Remove non-breaking space characters in the HTML
            html = html.replace('&nbsp;', ' ')

            return html


    # Create a list of HTML pages
    warn_pages = []
    counter = 0
    for link in tqdm(links):
        counter += 1
        html = get_page(link)
        warn_pages.append(html)
    # print(counter)

    
        
        
        # DON"T FORGET TO SLEEP FOR A BIT!
        # rest for a quarter second
        # This is really really im
        time.sleep(1)
        
    print('done fetching data')


    import re

    def parse_warn_page(html, url, notice_name):



        # Create a dictionary to store the data for a single WARN listing
        page_data = {'URL': url}
    #     print(page_data)

        # Make the soup for the single page
        page_soup = BeautifulSoup(html, 'html.parser')
    #     counter += 1

        # Sanity check
        # print(page_soup.prettify())

        # Get the first table (there should only be one)
        table = page_soup.table

        # Get all text in the table
        # get_text() will get all text in all elements underneath the current element, 
        # in this case all of the text in the <p> tags
        table_text = table.get_text()

        # Use a regular expression to throw away some extra info we don't care about
    #     table_text = re.split('(?:Additional|Other|Location).*', table_text)[0]

        # Split the text into a list of lines based on the newline character '\n'
        lines = table_text.split('\n')

        # Iterate over each line
        for line in lines:
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
    #             print(value)

                # The County data is formatted weirdly, using | to delimit some columns we want in our data
                try:
                    if key == 'County':
                        
                        split_row = value.split('|')
                        page_data['County'] = split_row[0]
                        for loc_data in split_row[1:]:
    #                         print(loc_data)
                            split_loc_data = loc_data.split(':')
    #                         print(split_loc_data)
                            
                            #these lines below fixed it
                            if len(split_loc_data) > 1:
                                key = split_loc_data[0]
                                value = split_loc_data[1]
                                page_data[key] = value
                            
                except IndexError:
    #                 print(counter)
                    print(" *****************************************************sjdlkfaj;selfj;lksjdflkasjlkfj;klasj;flaslkdfj")
                    
                            

        

        
        return page_data


    # # Create a list to store the data we scrape.
    # # Each item in the list will correspond to a single WARN listing
    # # Each column will be a piece of single labeled piece information from the listing
    data = []
    list = []

    for html_page, link, notice_name in zip(warn_pages, links, titles):
        if link not in list:
            try:
                page_data = parse_warn_page(html_page, link, notice_name)
                data.append(page_data)
            except TypeError:
                print(link)
        
    df = pd.DataFrame(data)

    cleaned = df[['URL', 'Date of Notice', ' Event Number', 'Rapid Response Specialist',
        'Reason Stated for Filing', 'Company', 'County', 'WDB Name', ' Region',
        'Contact', 'Phone', 'Business Type', 'Number Affected',
        'Total Employees', 'Layoff Date', 'Closing Date',
        'Reason for Dislocation', 'FEIN NUM', 'Union', 'Classification',
        ]]

    titles_and_urls = {'notice_title': titles, 'URL':links}
    titles_df = pd.DataFrame(titles_and_urls)
    # titles_df

    merged_file = cleaned.merge(titles_df, on='URL')
    final_df = merged_file[['notice_title','URL', 'Date of Notice', ' Event Number', 'Rapid Response Specialist',
        'Reason Stated for Filing', 'Company', 'County', 'WDB Name', ' Region',
        'Contact', 'Phone', 'Business Type', 'Number Affected',
        'Total Employees', 'Layoff Date', 'Closing Date',
        'Reason for Dislocation', 'FEIN NUM', 'Union', 'Classification',
        ]]

    final_df['New Notice'] = final_df['Date of Notice'].str.strip(' ')
    final_df['Amended'] = final_df['New Notice'].str.split(' ', 1)
    final_df['Amended'] = final_df['Amended'].apply(lambda x: x[1] if len(x) > 1 else '')
    final_df.drop(columns='New Notice', inplace = True)

    years_2015to2019 = pd.read_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/warn_scraper/process/years_2015to2019.csv')
    all_ny_warn = pd.concat([final_df, years_2015to2019])
    all_ny_warn.to_csv('/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/newyork_warn_raw.csv')


if __name__ == '__main__':
    newyork()