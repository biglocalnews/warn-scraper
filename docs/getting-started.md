# Getting started

## Install

Use `pip` or `pipenv` to install the Python library and command-line interface:

```bash
pipenv install git+ssh://git@github.com/biglocalnews/WARN.git#egg=WARN
```

## Usage

After you can use the command-line tool to scrape available states *by supplying one or more two-letter state postal codes*. The `warn-scraper` command-line tool will write files, by default, to a hidden directory in the user's home directory. On Apple and Linux systems, this will be `~/.warn-scraper`.

```bash
# Scrape a single state
warn-scraper AK

# Scrape multiple states
warn-scraper AK CT
```

To use the `warn` library in Python:

```python
>>> # Scrape Alaska to the default download directory
>>> from warn.scrapers import ak
>>> ak.scrape()
```

### Configuration

You can set the `WARN_OUTPUT_DIR` environment variable to specify a different download location.

Use the `--help` flag to view additional configuration and usage options:

```bash
warn-scraper --help

Usage: python -m warn [OPTIONS] [STATES]...

  Command-line interface for downloading WARN Act notices.

  STATES -- a list of one or more state postal codes to scrape. Pass `all` to
  scrape all supported states.

Options:
  --data-dir PATH                 The Path were the results will be saved
  --cache-dir PATH                The Path where results can be cached
  --upload / --no-upload          Upload generated files to BLN platform
                                  project
  --delete / --no-delete          Upload generated files to BLN platform
                                  project
  -l, --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the logging level
  --help                          Show this message and exit.
```

## Platform uploads

To upload data files to a project on the [Big Local News](https://biglocalnews.org/) platform,
you must set the `BLN_API_KEY` and `WARN_PROJECT_ID` environment variables.

Once the environment variables are configured, you can upload files using the `--upload` flag:

```bash
warn-scraper --upload AK
```

To avoid uploading files from previous runs, use the `--delete` flag to clear locally generated
cache as the first step in a new scraper run.

```bash
warn-scraper --delete --upload AK
```
