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
                        index_title = list(element.find('div', class_='indexTitle').children)
                        company_name = element.find("a", class_="bodylinks").text.strip() # strange white
                        # print(company_name) #space between items

                except:
                    # print('ELEMENT ', element)
                    a = 'a'

                try:
                    details = element.find("p").text

                    pattern = re.compile("""
                        (?P<category>.*) #grabs the type of notice
                        \s-\sCit(?:y|ies):?\s #identifies city/cities
                        (?P<city>.*)
                        ,\sCount(?:y|ies)(?:\sName)?:?\s
                        (?P<county>.*)
                        ,\s
                        (?P<unit>Number\w?|Program\w?)
                        \sAffected[:|;|\s]
                        (?P<count>.*)
                        """, re.VERBOSE)
                    match = re.search(pattern, details)
                    category, city, county, unit, count = match.groups()
                    # print(details)

                except:
                    details = element.find("span").text

                    # use this:
                    try:
                        pattern = re.compile("""
                            (?P<category>.*) #grabs the type of notice
                            \s-\sCit(?:y|ies):?\s #identifies city/cities
                            (?P<city>.*)
                            ,\sCount(?:y|ies)(?:\sName)?:?\s
                            (?P<county>.*)
                            ,\s
                            (?P<unit>Number\w?|Program\w?)
                            \sAffected[:|;|\s]
                            (?P<count>.*)
                            """, re.VERBOSE)
                        match = re.search(pattern, details)
                        category, city, county, unit, count = match.groups()

                        # This errors out
                        # Try it in Pythex
                    except:
                        print(details)
                        print(index_title[3])
                        print('------')
                        print(' ')
                        # a = 'This is fun'

                        # This returns none


# Output for this script currently prints out only the lines that have not been properly parsed by the REGEX.
                    


                    


main()

