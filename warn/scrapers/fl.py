#import csv
import datetime
import logging
import requests
import urllib3

from bs4 import BeautifulSoup
import pdfplumber
from retrying import retry

from warn.cache import Cache
from warn.utils import write_rows_to_csv

logger = logging.getLogger(__name__)


# first: go to URL http://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices
# next: gather all the links on the page (rather than hard-coding years)
# TODO next: scrape each link
# TODO gather each of the pages on that page (try to follow any link with only text '>' until u cant no more)
def scrape(output_dir, cache_dir=None):
    output_csv = '{}/fl.csv'.format(output_dir)
    cache = Cache(cache_dir)  # ~/.warn-scraper/cache
    # FL site requires realistic User-Agent.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    url = 'http://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices'
    response = requests.get(url, headers=headers, verify=False)
    logger.debug(f"Request status is {response.status_code} for {url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    # find & visit every year's WARN page
    links = soup.findAll('a', href=re.compile(
        '^http://reactwarn.floridajobs.org/WarnList/'))
    for link in links:
        link = link.get('href')  # get URL from link
        # some years link to pdf files only
        if 'pdf' in link.text:
            pdf = scrape_pdf(cache, link.text, headers)
        else:
            # TODO returns array of text to process
            html_pages = scrape_page(cache, link.text, headers)

    # OLD CODE BELOW
    # Remove later
    # V
    # V
    years = ['2019', '2020', '2021']
    # Load for first time => get header
    year = 2020
    page = 1
    html = find_page(cache, year, page)
    soup = BeautifulSoup(html, 'html.parser')
    soup.findAll('a', href=re.compile(
        '^http://reactwarn.floridajobs.org/WarnList/'))
    table = soup.find_all('table')  # output is list-type
    len(table)
    # find header
    first_row = table[0].find_all('tr')[0]
    headers = first_row.find_all('th')
    output_header = []
    for header in headers:
        output_header.append(header.text.strip())
    # save header
    write_rows_to_csv([output_header], output_csv)

    # NB: still fails to capture all information
    # e.g. gets Macy's but not store address,
    # layoff date skips "thru 03-30-20"
    # in fact, that text isnt captured by any html
    # am i reading it in poorly? is beautiful soup reading it in wrong?
    # html5lib works. what's different between html5lib and html.parser
    for year in years:
        if year == '2020':
            pages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                     14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        elif year == '2019':
            pages = [1, 2, 3, 4]
        for page in pages:
            html = find_page(cache, year, page)
            soup = BeautifulSoup(html, 'html5lib')
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
            write_rows_to_csv(output_rows, output_csv, 'a')
    return output_csv


@retry(
    stop_max_attempt_number=7,
    stop_max_delay=30000,
    wait_exponential_multiplier=2000,
    wait_exponential_max=10000
)
# TODO remember to traverse each page with '>'!
# TODO remove page, only track current url
def scrape_html(cache, year, url, headers):
    # sidestep SSL error
    urllib3.disable_warnings()
    # Add the state postal as cache key prefix
    html_cache_key = f'fl/{year}-{page}'
    current_year = datetime.date.today().year
    last_year = current_year - 1
    page_text = []

    # always re-scrape current year and prior year just to be safe
    if year == current_year or year == last_year:
        response = requests.get(url, headers=headers, verify=False)
        logger.debug(f"Request status is {response.status_code} for {url}")
        response.raise_for_status()
        logger.debug(f"Successfully scraped {url}")
        page_text.append(response.text)
        # cache.write(html_cache_key, page_text)
        logger.debug(f"Scraped page cached to: {html_cache_key}")
    else:
        try:
            page_text.append(cache.read(html_cache_key))
            logger.debug(f'Page fetched from cache: {html_cache_key}')
        except FileNotFoundError:
            response = requests.get(url, headers=headers, verify=False)
            logger.debug(f"Request status is {response.status_code} for {url}")
            response.raise_for_status()
            logger.debug(f"Successfully scraped {url}")
            page_text.append(response.text)
            cache.write(html_cache_key, page_text)
            logger.debug(f"Scraped page cached to: {html_cache_key}")
    # traverse to next page
    soup = BeautifulSoup(response.text, 'html.parser')
    nextPageLink = soup.findAll('a', string=re.compile(f'^>$'))
    if(nextPageLink):
        url = nextPageLink.get('href')
        page_text.append(scrape_html(cache, year, url, headers))


def scrape_pdf(cache, year, page, headers):
    # try: find pdf in cache. process in pandas(?), and return as output_csv
    # except: download pdf, store in cache, process in pandas(?), and return as output_csv
    url = f'http://reactwarn.floridajobs.org/WarnList/viewPreviousYearsPDF?year={year}'
    response = requests.get(url, headers=headers, verify=False)
    logger.debug(f"Request status is {response.status_code} for {url}")
    response.raise_for_status()
    with pdfplumber.open("path/to/file.pdf") as pdf:
    first_page = pdf.pages[0]
    print(first_page.chars[0])
    logger.debug(f"Successfully scraped {url}")
    return processed_pdf
