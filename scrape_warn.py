import argparse
import re
import os
import sys
from importlib import import_module

# Top-Level CLI script

def main(states):

    args = create_argparser()
    output_dir = args.output_dir[0]
    states = args.states

    if args.all:
        run_scraper_for_all_states(output_dir)
    else:
        for state in states:
            scrape_warn_sites(state, output_dir)

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
    my_parser.add_argument('--states', '-s', help='one or more state postals', nargs='+', action='store')
    my_parser.add_argument('--all', '-a',action='store_true', help='run all scrapers' )

    args = my_parser.parse_args()
    return args

def scrape_warn_sites(state, output_dir):
    state_clean = state.strip().lower()
    state_mod = import_module('warn.scrapers.{}'.format(state_clean))
    state_mod.scrape(output_dir)

def run_scraper_for_all_states(output_dir):
    print('Scraping all warn notices')
    dirs = os.listdir('warn/scrapers/')
    for state in dirs:
        if not state.startswith('.'):
            state = state[0:2]
            scrape_warn_sites(state, output_dir)


if __name__ == '__main__':
    states  = sys.argv[1:]
    main(states)
