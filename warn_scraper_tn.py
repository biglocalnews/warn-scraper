from os import path
import pathlib

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import json

import re

# spot-checked and linked-checked
# scraper looks good

root = pathlib.Path(__file__).parent.resolve()

def tennessee():
    output_csv = root / 'data' / 'tennessee_warn_raw.csv'
    #output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/tennessee_warn_raw.csv'
    url = 'https://www.tn.gov/workforce/general-resources/major-publications0/major-publications-redirect/reports.html'

    page = requests.get(url)
    print(page.status_code) # should be 200
    soup = BeautifulSoup(page.text, 'html5lib')

    output_header = [
        "Date Notice Posted",
        "Company",
        "County",
        "Affected Workers",
        "Closure/Layoff Date",
        "Notice/Type"
    ]

    div = soup.find_all("div", {"class": "tn-rte parbase"})

    p_list = div[0].find_all("p")
    p_list = p_list[0:len(p_list)-1] # remove "For Previous WARN Notices" message

    output_rows = []
    excluded_rows = []
    for p in p_list:
        p_ind = p.text
        p_ind_list = p_ind.split("|")
        # p_ind_list = [x.strip() for x in p_ind_list]
        
        if len(p_ind_list) == 6:
            output_row = []
            # for future, use dict instead of array so it doesnt have to be manually in order
            output_row.append(re.search('Date Notice(d)? Posted( )?:(.*)$', p_ind_list[0]).group(3))
            output_row.append(re.search('Company:(.*)$', p_ind_list[1]).group(1))
            output_row.append(re.search('(County|Counties):(.*)$', p_ind_list[2]).group(2))
            output_row.append(re.search('Affec(c)?ted Workers:(.*)$', p_ind_list[3]).group(2))
            output_row.append(re.search('Closure/Layoff Date:(.*)$', p_ind_list[4]).group(1))
            output_row.append(re.search('Notice(/| )Type:(.*)$', p_ind_list[5]).group(2))
            output_row = [x.strip() for x in output_row]
            
            # print(output_row)
            output_rows.append(output_row)
        else:
            print("Error: row != 6 items")
            print("Row: {}".format(p_ind_list))
            excluded_rows.append(p_ind_list)


    print(excluded_rows)

    # manually add excluded rows
    output_rows.append([
        "2018/12/5", "Emergency Mobile Health Care, LLC", "", "207", "February 1, 2019", "#20180036"
    ])
    output_rows.append([
        "2018/2/22", "Whelan Security Company", "Rutherford", "95", "April 1, 2018", "#2018007"
    ])
    output_rows.append([
        "2018/2/12", "Ebuys, Inc. dba Shoe Metro (She Metro)", "Rutherford", "172", "April 6, 2018", "#2018006"
    ])
    output_rows.append([
        "2018/2/8", "Global Personnel Soultions, Inc.", "Bradley", "202", "February 8, 2018", "#2018005"
    ])
    output_rows.append([
        "2018/1/30", "Radial South", "Shelby", "486", "April 7, 2018", "#2018004"
    ])

    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)
        writer.writerows(output_rows)

if __name__ == '__main__':
    tennessee()
