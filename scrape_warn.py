# import argparse
import re
import os
import sys
from importlib import import_module


def main(states):
    
    if 'all' or 'ALL' in states:
        print('Scraping all warn notices')
        dirs = os.listdir('warn/scrapers/')
        for state in dirs:
            if not state.startswith('.'):
                state = state[0:2]
                scrape_warn_sites(state)

    else:
        for state in states:
            scrape_warn_sites(state)
            

def scrape_warn_sites(state):

    state_clean = state.strip().lower()
    state_mod = import_module('warn.scrapers.{}'.format(state_clean))
    state_mod.scrape()


if __name__ == '__main__':
    states  = sys.argv[1:]
    main(states)
