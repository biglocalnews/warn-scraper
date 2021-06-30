## Overview

This project provides a library and command-line tool for scraping WARN (layoff) Notices from several state sites.

- [Install](#install)
- [Usage](#usage)
- [Platform uploads](#platform-uploads)
- [Developers](#developers)

## Install

> If you're contributing code, see the [Developer docs](#developers) below for alternative install and usage information.

Use `pip` or `pipenv` to install the WARN Python library and CLI tool for normal day-to-day use:

```bash
pip install git+ssh://git@github.com/biglocalnews/WARN.git#egg=WARN
# or
pipenv install git+ssh://git@github.com/biglocalnews/WARN.git#egg=WARN
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

To use the `warn` library in a Python script:

```python
# myscript.py

# Scrape Alaska
from warn.scrapers import ak

# Specify cache and final export dirs (these should be different)
export_dir = '/tmp/warn/ak/exports' # final CSV written here
cache_dir = '/tmp/warn/ak/cache'    # for any files used in processing

ak.scrape(export_dir, cache_dir)
```

### Configuration

The `warn-scraper` command-line tool will write files, by default, to a hidden directory in the user's home directory.

On Mac/Linux systems, this will be `~/.warn-scraper`.

You can set the `WARN_ETL_DIR` environment variale to specify a different location.

Use the `--help` flag to view additional configuration and usage options:

```bash
warn-scraper --help
```

## Platform uploads

To upload data files to a project on the [Big Local News](https://biglocalnews.org/) platform,
you must set the `BLN_API_KEY` and `WARN_PROJECT_ID` environment variables.

Once the environment variables are configured, you can upload files using the `--upload` flag:

```bash
warn-scraper --upload -s AK
```

> NOTE: All files generated during a scrape are uploaded at the end of a scraper run.

To avoid uploading files from previous runs, use the `--delete` flag to clear locally generated
files *as the first step* in a new scraper run.

```bash
warn-scraper --delete --upload -s AK
```

## Developers

If you're contributing code to this project, the general workflow is to:

* Create a GitHub issue related to your feature or bugfix
* Perform your work on a branch created from `main`
* Push code to *your own branch*
* On GitHub, send a Pull Request from your branch to `main`
* Ping a BLN team member to review and merge your work

### Install from GitHub

Install [pipenv](https://docs.pipenv.org/en/latest/basics.html#installing-pipenv).

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

### GitHub cheatsheet

Below are some reminders on commands that can be helpful for our branch-oriented Git/GitHub workflow.

When starting a new branch:

```bash
# Checkout main and pull to make sure you have the latest code
git checkout main
git pull

# Create a branch using <state>-<issue #> pattern
git checkout -b nj-100
```

When pushing a branch for the first time:

```bash
git push -u origin nj-100
```

When you need to pull in the latest changes from `main`:

```bash
# Stash or commit the work on your active branch
git stash

# Checkout and pull updates on main
git checkout main
git pull

# Checkout your branch
git checkout nj-100

# Rebase your changes on top of main
git rebase main

# Re-apply stashed changes, if any
git stash apply
```

After a rebase, delete and recreate your *remote* branch (if you previously pushed it):

```bash
# Delete the branch on the remote called origin
git push origin :nj-100

# Push the branch anew (after you've rebased)
git push -u origin nj-100
```

To clean up your local list of remote branches that have been merged and deleted (during
the Pull Request process):

```bash
# To view references to remote branches
git branch -a

# If there are remote branches that no longer exist
# (i.e were deleted as part of a Pull Request merge),
# you can "prune" those local references
git remote prune origin
```
