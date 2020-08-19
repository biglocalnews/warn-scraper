import csv
import logging
import requests

from bs4 import BeautifulSoup

# spot-check once more

def scrape(output_dir):
    
    logger = logging.getLogger(__name__)
    output_csv = '{}/washington_warn_raw.csv'.format(output_dir)
    # pages = range(2, 60, 1)
    page = 2

    url = 'https://fortress.wa.gov/esd/file/warn/Public/SearchWARN.aspx'

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:68.0) Gecko/20100101 Firefox/68.0"}
    with requests.Session() as session:
        # initial get
        response_initial = session.get(url, headers = headers) #, data = formdata)
        logger.info(response_initial.status_code)
        soup_content = BeautifulSoup(response_initial.content, 'html5lib')
        soup_text = BeautifulSoup(response_initial.text, 'html5lib')
        table = soup_text.find_all('table') # output is list-type
        
        # find and write header
        first_row = table[0].find_all('tr')[2]
        table_headers = first_row.find_all('th')
        output_header = []
        for table_header in table_headers:
            output_header.append(table_header.text)
        output_header = [x.strip() for x in output_header]
        
        with open(output_csv, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(output_header)
        
        # find and write first page
        output_rows = []
        for table_row in table[0].find_all('tr'):    
            columns = table_row.find_all('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_row = [x.strip() for x in output_row]
            output_rows.append(output_row)
        output_rows = output_rows[3:len(output_rows)-2]
        
        with open(output_csv, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)
        
        while True:
            try:


                formdata = {
                    '__EVENTTARGET': 'ucPSW$gvMain',
                    '__EVENTARGUMENT': 'Page${}'.format(page),
                    '__VIEWSTATE': soup_content.find('input', attrs={'name': '__VIEWSTATE'})['value'],
                    '__EVENTVALIDATION': soup_content.find('input', attrs={'name': '__EVENTVALIDATION'})['value']
                }
            
                response_next = session.post(url, data = formdata)
                logger.info(response_next.status_code) # should be 200
                soup_content = BeautifulSoup(response_next.content, 'html5lib')
                soup_text = BeautifulSoup(response_next.text, 'html5lib')
                table_next = soup_text.find_all('table') # output is list-type

                output_rows = []
                for table_row in table_next[0].find_all('tr'):    
                    columns = table_row.find_all('td')
                    output_row = []
                    for column in columns:
                        output_row.append(column.text)
                    output_row = [x.strip() for x in output_row]
                    output_rows.append(output_row)
                output_rows = output_rows[3:len(output_rows)-2]
                # first row of page
                
                with open(output_csv, 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(output_rows)
                page += 1

            except:
                break
            
    logger.info("WA successfully scraped.")



if __name__ == '__main__':
    scrape()