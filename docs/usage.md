# Usage

You can use the `warn-scraper` command-line tool to scrape available states by supplying one or more two-letter state postal codes. It will write files, by default, to a hidden directory in the user's home directory. On Apple and Linux systems, this will be `~/.warn-scraper`.

```bash
# Scrape a single state
warn-scraper AK

# Scrape multiple states
warn-scraper AK CT
```

To use the `warn` library in Python, import a state's scraper and run it directly.

```python
from warn.scrapers import ak

ak.scrape()
```

## Configuration

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
  --delete / --no-delete          Delete generated files from the cache
  -l, --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the logging level
  --help                          Show this message and exit.
```
