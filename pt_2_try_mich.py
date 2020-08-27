import csv
import logging
import re
import requests
import time

from bs4 import BeautifulSoup
from bs4 import NavigableString

def main():
    # year_list = [2014, 2015, 2016, 2017, 2018, 2019, 2020]
    year_list = [2016, 2017]
    month_list = ["December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"]

    for year in year_list:
        year = str(year)
        url = 'https://www.michigan.gov/leo/0,5863,7-336-78421_95539_64178_64179---Y_{},00.html'.format(year)

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html5lib')

        month_headers = soup.find_all("div", class_="row archive-year-section")

        for month_element in month_headers:
            print("Month Element {}".format(month_element.text))

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

            # print(month_data)
            output_rows = []
            for element in month_data:
                try:

                    extra_info = element.find("p").text
                    extra_string = 'WARN notices are required by the Federal Worker Adjustment and Retraining Notification'
                    if extra_string in extra_info:
                        continue
                    else:
                        day = element.find("div", class_="meDate").text
                        date = ' '.join([day, month_element.text, year])
                        company_name = element.find("a", class_="bodylinks").text.strip() # strange white space between items

                except:
                    print('ELEMENT ', element)

                try:
                    details = element.find("p").text
                    details = details.replace('<br/>', '') #doesn't change anything
                except:
                    details = element.find("span").text
                    details = details.replace('<br/>', '') #doesn't change anything

                try: 
                    closure_type = re.search('(Layoff|Closure|Closing|LayOff)', details).group()

                    city = re.search('(City:|Cities:|City)(.*)(County|Couny|Counties|County Name)', details).group(2).strip()
                    if city[len(city)-1] in [",", ";"]:
                        city = city[0:len(city)-1]

                    county = re.search('(County:|County |Couny:|Counties:|County Name:)(.*)(Number|Numbers|Total Number|Program|Programs)(.*)(Affected|Affercted|of Affected)', details).group(2).strip()
                    if county[len(county)-1] == ",":
                        county = county[0:len(county)-1]
                    # else:
                    #     county = 'multiple counties'

                    # print('City ', city)
                    # print(element)
                except:
                    print('NO CITY ', element)
                    print(details)
                    a = 'a'
         





# def extract_div_data(div_element):

#     month_list = ["December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"]

#     data = div_element.find("a")["title"]
#     print(data)


main()

