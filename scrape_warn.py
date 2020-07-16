# import argparse
from importlib import import_module
import sys


def main(states):
    for state in states:
        # TODO: Aggressive exception handling here
        # (and alerting)
        import ipdb
        ipdb.set_trace()
        state_clean = state.strip().lower()
        state_mod = import_module('warn.scrapers.{}'.format(state_clean))
        state_mod.scrape()

if __name__ == '__main__':
    states  = sys.argv[1:]
    main(states)
