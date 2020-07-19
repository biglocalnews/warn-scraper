# import argparse
import re
import os
import sys
from importlib import import_module

# Top-Level CLI script

def main(states):

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    if '--output-dir' in opts[0]:
        output_dir = opts[0].split('=')[1]
        states = states[:-1]

        if 'all' in states or 'ALL' in states:
            run_scraper_for_all_states(output_dir)
        else:
            for state in states:
                scrape_warn_sites(state, output_dir)
            

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
