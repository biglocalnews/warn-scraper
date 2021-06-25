## Overview

This project provides a library and command-line tool for scraping WARN (layoff) Notices from several state sites.

- [Install](#install)
- [Usage](#usage)
- [Developers](#developers)

## Install

> If you're contributing code, see the [Developer docs](#developers) below for alternative install and usage information.

Use `pip` or `pipenv` to install the WARN Python library and CLI tool for normal day-to-day use:

```bash
pip install git+ssh://git@github.com/biglocalnews/WARN.git@prefect#egg=WARN
# or
pipenv install git+ssh://git@github.com/biglocalnews/WARN.git@prefect#egg=WARN
```

## Usage

After [installation](#install),  you can use the command-line tool to scrape available states *by supplying one or more two-letter state postal codes*.

> See the [`warn/scrapers/`][] directory for available state modules.

[`warn/scrapers/`]: https://github.com/biglocalnews/WARN/tree/main/warn/scrapers

```bash
# Scrape a single state
warn-scraper -s AK

# Scrape multiple states
warn-scraper -s AK CT
```

For additional configuration options:

```bash
warn-scraper --help
```

## Developers

If you're contributing code to this project, the general workflow is to:

* Create a GitHub issue related to your feature or bugfix
* Perform your work on a branch created from `main`
* Push code to *your own branch*
* On GitHub, send a Pull Request from your branch to `main`
* Ping a BLN team member to review and merge your work

### Install from GitHub

```bash
git clone git@github.com:biglocalnews/WARN.git
cd WARN/
pipenv install
```

### Dev CLI usage

The WARN command-line tool provides a handy way to "manually" test code changes for a given state.

However, using the CLI command **in a development context** is a bit trickier compared to normal usage, due to the nature of how we've ["packaged"](https://packaging.python.org/tutorials/packaging-projects/) this project as an installable library and command-line tool.

Gory details aside, here's how to run the command-line tool when developing code:

> **IMPORTANT**: The below commands will *only* work from the root of the project!

```bash
# Navigate to repo's root folder
cd WARN/

# Activate the virtual environment
pipenv shell

# Invoke the cli.py module
python -m warn.cli -s AK

# For more detailed debugging output, use the -l flag
python -m warn.cli -l DEBUG -s AK
```