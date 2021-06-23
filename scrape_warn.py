import argparse
import logging
import re
import os
import sys
import traceback

from importlib import import_module
from pathlib import Path

from alerts import SlackAlertManager
from warn_uploads import upload
from remove_data import delete_files

ETL_DIR=os.environ.get('WARN_ETL_DIR', '/tmp/etl/WARN')
PROCESS_DIR=os.environ.get('PROCESS_DIR', Path(ETL_DIR, 'process'))
WARN_DATA_PATH=os.environ.get('WARN_DATA_PATH', Path(ETL_DIR, 'warn'))
WARN_LOG_PATH=os.environ.get('WARN_LOG_PATH', Path(ETL_DIR, 'logs'))

for d in [PROCESS_DIR, WARN_DATA_PATH, WARN_LOG_PATH]:
    Path(d).mkdir(parents=True, exist_ok=True)

# Logging setup
log_file = os.path.join(WARN_LOG_PATH, 'warn-scraper.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-12s - %(message)s',
    datefmt='%m-%d %H:%M',
    filename=log_file,
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

# Argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '--output-dir',
    help='Directory where final outputs will be written',
    action='store',
    type=str,
    default=WARN_DATA_PATH
)
parser.add_argument(
    '--cache-dir',
    help='Directory where intermediate ETL files should we written',
    action='store',
    default=ETL_DIR
)
parser.add_argument('--states', '-s', help='One or more state postals', nargs='+', action='store')
parser.add_argument('--all', '-a',action='store_true', help='Run all scrapers')
parser.add_argument('--alert',action='store_true', help='Send scraper status alerts to Slack.')


def main(states, output_dir, cache_dir, alert):
    alert_manager=None
    if alert:
        try:
            api_key = os.environ['SLACK_API_KEY']
            channel = os.environ['SLACK_ALERTS_CHANNEL']
            alert_msg = "Slack alerts will be sent to #{}.".format(channel)
            alert_manager = SlackAlertManager(api_key, channel)
        except KeyError:
            alert_msg = "WARNING - Slack alerts will not be sent.\n" + \
                "Please ensure you've configured the below environment variables:\n" + \
                "SLACK_API_KEY=YOUR_API_KEY\n" + \
                "SLACK_ALERTS_CHANNEL=channel-name\n\n"
        finally:
            logger.warning(alert_msg)
    states_failed = []
    traceback_msg = []
    if args.all:
        error_states, traceback_str = run_scraper_for_all_states(output_dir, cache_dir, alert, logger, states_failed, traceback_msg)
        states_not_scraped(states_failed, error_states, traceback_msg, traceback_str)
    else:
        for state in states:
            error_states, traceback_str = scrape_warn_site(state, output_dir, cache_dir, alert, logger)
            states_not_scraped(states_failed, error_states, traceback_msg, traceback_str)
    logged_info = upload(output_dir)
    delete_files(output_dir)
    if alert:
        slack_messages(alert, alert_manager, states_failed, traceback_msg, states, logger)
        slack_messages_two(alert, alert_manager, logged_info)


def scrape_warn_site(state, output_dir, cache_dir, alert, logger):
    not_scraped = []
    scraped_site = []
    state_clean = state.strip().lower()
    state_mod = import_module('warn.scrapers.{}'.format(state_clean))
    try:
        state_mod.scrape(output_dir)
        scraped_site.append(state_clean)
        traceback_str = 'No errors in scraping.'
    except Exception as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        logger.error('{} scraper did not run.'.format(state_clean))
        logger.error(traceback_str)
        not_scraped.append(state_clean)
    finally:
        return not_scraped, traceback_str

def run_scraper_for_all_states(output_dir, cache_dir, alert, logger, states_failed, traceback_msg):
    logger.info('Scraping all warn notices')
    dirs = os.listdir('warn/scrapers/')
    for state in dirs:
        if not state.startswith('.'):
            state = state[0:2]
            error_states, traceback_str = scrape_warn_site(state, output_dir, cache_dir, alert, logger)
    return error_states, traceback_str


def slack_messages(alert, alert_manager, states_failed, traceback_msg, states, logger):
    if alert and alert_manager:

        if states == None:
            count = 0
            states_list = []
            dirs = os.listdir('warn/scrapers/')
            for state in dirs:
                if not state.startswith('.'):
                    state = state[0:2].upper()
                    states_list.append(state)
                    count += 1
            count_of_states_run = count - len(states_failed)
            successfully_run = list(set(states_list) - set(states_failed))
        else:
            count_of_states_run = len(states) - len(states_failed)
            successfully_run = list(set(states) - set(states_failed))
        successfully_run = ', '.join(map(str, successfully_run))
        overall_state_msg = '{} scraper(s) ran successfully: {}'.format(count_of_states_run, successfully_run)
        logger.info(overall_state_msg)
        alert_manager.add(overall_state_msg, 'INFO')

        for fail in traceback_msg:

            logger.error(fail)
            alert_manager.add(fail, 'ERROR')


def slack_messages_two(alert, alert_manager, logged_info):
    if alert and alert_manager:

        for file in logged_info:
            alert_manager.add(file, 'INFO')
    alert_manager.send()


def states_not_scraped(states_failed, error_states, traceback_msg, traceback_str):
    if error_states != []:
        error_states = [x.upper() for x in error_states]
        states_failed.append(error_states[0])
        traceback_msg.append(traceback_str)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args.states, args.output_dir, args.cache_dir, args.alert)
