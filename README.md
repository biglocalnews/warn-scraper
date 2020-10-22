## Overview

This project provides a command-line tool for scraping WARN (layoff) Notices from several state sites. 
Currently, we are scraping the sites of 21 states, and will be adding more as we continue to build out this tool.

## Install

To install, git clone the link of the repo

`git clone git@github.com:biglocalnews/WARN.git`

To start using the tool, activate the environment

`pipenv shell` 


## Usage

Once the environment is activated, you may use a number of commands to run the scripts.

To see the available commands:

`python scrape_warn.py -h`

You will see instructions on how to proceed:

```

usage: scrape_warn.py [-h] [--output-dir OUTPUT_DIR [OUTPUT_DIR ...]] [--cache-dir CACHE_DIR [CACHE_DIR ...]] [--states STATES [STATES ...]] [--all]
                      [--alert]

optional arguments:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR [OUTPUT_DIR ...]
                        specify output directory
  --cache-dir CACHE_DIR [CACHE_DIR ...]
                        specify log dir
  --states STATES [STATES ...], -s STATES [STATES ...]
                        one or more state postals
  --all, -a             run all scrapers
  --alert               Send scraper status alerts to Slack.

```


### Basic Commands

To run one scraper:

`python scrape_warn.py -s UT`

To run multiple, but not all scrapers:

`python scrape_warn.py -s UT AL CA RI`

To run all scrapers:

`python scrape_warn.py -a`


### With Alerts

To run one scraper:

`python scrape_warn.py -s UT --alert`

To run multiple, but not all scrapers:

`python scrape_warn.py -s UT AL CA RI --alert`

To run all scrapers:

`python scrape_warn.py -a --alert`


### With Specified File Paths

To run one scraper:

`python scrape_warn.py -s UT --output-dir=/home/computer/file/path --alert`

To run multiple, but not all scrapers:

`python scrape_warn.py -s UT AL CA RI --output-dir=/home/computer/file/path --alert`

To run all scrapers:

`python scrape_warn.py -a --cache-dir=/home/computer/file/path/to/logs --alert`


