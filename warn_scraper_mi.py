from os import path
import pathlib

import csv 
from datetime import datetime

from bs4 import BeautifulSoup
from bs4 import NavigableString

import requests
import json

import re


# spot-checked and linked-checked
# scraper looks good

root = pathlib.Path(__file__).parent.resolve()

def michigan():
    
    output_csv = root / 'data' / 'michigan_warn_raw.csv'
    
    #output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/michigan_warn_raw.csv'
    year_list = range(2014, 2021, 1)
    month_list = ["December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"]
    # https://www.michigan.gov/leo/0,5863,7-336-78421_95539_64178_64179---Y_2020,00.html#April2020
    # url = 'https://www.michigan.gov/leo/0,5863,7-336-78421_95539_64178_64179---Y_2019,00.html'

    output_header = [
        "Date Notice Posted",
        "Company",
        "Closure Type",
        "City", 
        "County",
        "Number Affected"
    ]

    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)


    error_data = []

    for year in year_list:
        year = str(year)
        print(year)
        url = 'https://www.michigan.gov/leo/0,5863,7-336-78421_95539_64178_64179---Y_{},00.html'.format(year)

        page = requests.get(url)
        print(page.status_code) # should be 200
        soup = BeautifulSoup(page.text, 'html5lib')

        month_headers = soup.find_all("div", class_="row archive-year-section")

        for month_element in month_headers:
            print(month_element.text)

            month_data = []
            for element in month_element.next_siblings:
                if isinstance(element, NavigableString):
                    continue
                elif element.text in month_list:
                    break
                elif element['class'][0] == "row":
                    break
                else:
                    month_data.append(element)

            output_rows = []
            for element in month_data:
                try: 
                    day = element.find("div", class_="meDate").text
                    date = ' '.join([day, month_element.text, year])
                    company_name = element.find("a", class_="bodylinks").text.strip() # strange white space between items
                except AttributeError as err:
                    print("Attribute Error: {}".format(err))
                    error_data.append(element)

                try:
                    details = element.find("p").text
                except AttributeError as err:
                    print("Attribute Error for p: {}".format(err))
                    details = element.find("span").text

                try: 
                    closure_type = re.search('^(.*)(-)', details).group(1).strip()

                    city = re.search('(City:|Cities:|City)(.*)(County|Counties|County Name)', details).group(2).strip()
                    if city[len(city)-1] in [",", ";"]:
                        city = city[0:len(city)-1]

                    county = re.search('(County:|Counties:|County Name:)(.*)(Number|Numbers|Program|Programs) Affected', details).group(2).strip()
                    if county[len(county)-1] == ",":
                        county = county[0:len(county)-1]

                    number_affected = re.search('(Number|Numbers|Program|Programs) Affected(:|;| )(.*)', details).group(3).strip()

                    output_row = [date, company_name, closure_type, city, county, number_affected]
                    output_rows.append(output_row)
                except AttributeError as err:
                    print("Attribute Error: {}".format(err))
                    error_row = [date, company_name, details]
                    error_data.append(error_row)

            with open(output_csv, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)

    print(error_data)

    fixed_rows = []
    fixed_rows.append(['30 September 2014', 'Detroit Medical Center (DMC)', 'Closure', 'Madison Heights', 'Oakland', '127'])
    fixed_rows.append(['23 October 2015', 'FTE Automotive', 'Closure', 'Auburn Hills', 'Oakland', '85'])
    fixed_rows.append(['30 September 2016', 'Kmart - Sault Saint Marie', 'Closure', 'Sault Saint Marie', 'Chippewa', '47'])
    # fixed_rows.append(['12 September 2016', 'Midwest Medical Center'])
    fixed_rows.append(['14 August 2017', 'Great Lakes Wine & Spirits', 'Closure, Layoff, Layoff', 
                    'Petoskey, Traverse City, Gaylord', 'Emmet, Grand Traverse, Otsego', '101'])
    fixed_rows.append(['20 July 2017', 'Kindred Hospital - Detroit', 'Closure', 'Detroit', 'Wayne', '145'])
    fixed_rows.append(['06 March 2017', 'Yanfeng', 'Layoff', 'Lansing', 'Ingham', '27'])



    with open(output_csv, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(fixed_rows)

if __name__ == '__main__':
    michigan()
