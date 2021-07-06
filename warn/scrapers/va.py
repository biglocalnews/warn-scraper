import csv
import logging
import requests

from bs4 import BeautifulSoup

logger  = logging.getLogger(__name__)


def scrape(output_dir, cache_dir=None):
    output_csv = f'{output_dir}/va.csv'
    url = 'https://www.vec.virginia.gov/warn-notices'
    response = requests.get(url)
    logger.debug(f"Page status is {response.status_code} for {url}")
    soup = BeautifulSoup(response.text, 'html.parser')

    data_url = soup.find("a", text="Download")['href']
    data_url = f'https://www.vec.virginia.gov{data_url}'
    data= requests.get(data_url)
    decoded_content = data.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',', quotechar='"')

    with open(output_csv,'w') as csvfile:
        writer = csv.writer(csvfile)
        for line in cr:
            writer.writerow(line)

    return output_csv
