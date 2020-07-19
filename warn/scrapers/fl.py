import csv
import requests

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):

    # output_csv = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/florida_warn_raw.csv'
    output_csv = '{}/florida_warn_raw.csv'.format(output_dir)
    
    # max_entries = 378 # manually inserted
    # start_row_list = range(1, max_entries, 50)
    years = ['2019', '2020']

    # Load for first time => get header
    year = 2020
    page = 1
    url = 'http://reactwarn.floridajobs.org/WarnList/Records?year={}&page={}'.format(year, page)
    page = requests.get(url)

    print(page.status_code) # should be 200

    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find_all('table') # output is list-type
    len(table)

    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text)
    output_header = [x.strip() for x in output_header]
    output_header

    # save header
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_header)

    # NB: still fails to capture all information
    # e.g. gets Macy's but not store address, 
    # layoff date skips "thru 03-30-20"
    # in fact, that text isnt captured by any html
    # am i reading it in poorly? is beautiful soup reading it in wrong?
    # html5lib works. what's different between html5lib and html.parser

    for year in years:
        if year == '2020':
            pages = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
        elif year == '2019':
            pages = [1,2,3,4]
            
        for page in pages:
            url = 'http://reactwarn.floridajobs.org/WarnList/Records?year={}&page={}'.format(year,page)
            page = requests.get(url)
            print(page.status_code) # should be 200
            
            soup = BeautifulSoup(page.text, 'html5lib')

            table = soup.find_all('table')

            output_rows = []
            for table_row in table[0].find_all('tr'):    
                columns = table_row.find_all('td')
                output_row = []
                for column in columns:
                    output_row.append(column.text)
                output_row = [x.strip() for x in output_row]
                output_rows.append(output_row)
            output_rows.pop(0)
            output_rows.pop(0)

            with open(output_csv, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(output_rows)           

if __name__ == '__main__':
    scrape()
