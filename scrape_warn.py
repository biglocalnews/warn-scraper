import argparse
import logging
import re
import os
import sys

from alerts import SlackAlertManager
from importlib import import_module
from pathlib import Path

# Top-Level CLI script

def main(states):

    args = create_argparser()
    output_dir = args.output_dir[0]
    cache_dir = args.cache_dir[0]
    states = args.states
    alert = args.alert

    if args.all:
        run_scraper_for_all_states(output_dir, cache_dir, alert)
    else:
        for state in states:
            scrape_warn_site(state, output_dir, cache_dir, alert)

def create_argparser():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument(
        '--output-dir', 
        help='specify output directory', 
        action='store', 
        nargs='+', 
        type=str, 
        default=["/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/"]
        )
    my_parser.add_argument(
        '--cache-dir', 
        help='specify log dir', 
        action='store',
        nargs='+',
        default=["/Users/dilcia_mercedes/Big_Local_News/prog/WARN/logs/"]
        )
    my_parser.add_argument('--states', '-s', help='one or more state postals', nargs='+', action='store')
    my_parser.add_argument('--all', '-a',action='store_true', help='run all scrapers')
    my_parser.add_argument('--alert',action='store_true', help='Send scraper status alerts to Slack.')

    args = my_parser.parse_args()
    return args

def scrape_warn_site(state, output_dir, cache_dir, alert):

    log_file = os.path.join(cache_dir, 'log.txt')

    Path(cache_dir).mkdir(parents=True, exist_ok=True)
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

    alert_manager=None
    if alert:
        try:
            api_key = os.environ['WARN_SLACK_API_KEY']
            channel = os.environ['WARN_SLACK_CHANNEL']
            alert_msg = "Slack alerts will be sent to #{}.".format(channel)
            alert_manager = SlackAlertManager(api_key, channel)
        except KeyError:
            alert_msg = "WARNING - Slack alerts will not be sent.\n" + \
                "Please ensure you've configured the below environment variables:\n" + \
                "WARN_SLACK_API_KEY=YOUR_API_KEY\n" + \
                "WARN_SLACK_CHANNEL=channel-name\n\n"
        finally:
            logger.warning(alert_msg)

    state_clean = state.strip().lower()
    state_mod = import_module('warn.scrapers.{}'.format(state_clean))
    try:
        state_mod.scrape(output_dir)
        if alert and alert_manager:
            alert_manager.add('WARN Test', 'INFO')
            alert_manager.add('WARN Test 2', 'INFO')
            alert_manager.send()
    except Exception as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        logger.error('{} scraper did not run.'.format(state_clean))
        logger.error(traceback_str)

def run_scraper_for_all_states(output_dir, cache_dir, alert):
    print('Scraping all warn notices')
    dirs = os.listdir('warn/scrapers/')
    for state in dirs:
        if not state.startswith('.'):
            state = state[0:2]
            scrape_warn_site(state, output_dir, cache_dir, alert)


if __name__ == '__main__':
    states  = sys.argv[1:]
    main(states)
