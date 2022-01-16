# Contributing

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

### Tests

Testing is implemented via pytest. Run the tests with the following:

```bash
pipenv run pytest
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

# Fix merge conflicts if any (ping for help if needed)

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

### File name conventions

We should apply the following conventions to all state scrapers:

- Always use the **lower-case state postal code** in the name of "export" files intended to be uploaded to the Big Local News platform for end users. For example: `exports/nj.csv`
- States should generally have a single export file, unless there's a known edge case (e.g. CA).
- "Intermediate" files used for data processing should not be published to the BLN platform. Such files should be written to the `cache/` directory.
  - For simple cases, use a cache name identical to the final export name (e.g. `cache/mo.csv` and `exports/mo.csv`).
  - For more complex cases, use the state postal code plus a standard suffix (e.g. `cache/mo_raw_1.csv` , `cache_mo_raw_2.csv`).
  - If many files need to be cached, create a subdirectory using the lower-case state postal code and apply a sensible naming scheme to the cached files (e.g. `cache/mo/page_1.html`).

Here's an example directory demonstrating the above conventions:

```bash
├── cache
│   ├── mo.csv
│   ├── nj
│   │   ├── Jan2010Warn.html
│   │   └── Jan2011Warn.html
│   ├── ny_raw_1.csv
│   └── ny_raw_2.csv
└── exports
    ├── mo.csv
    ├── nj.csv
    └── ny.csv
```


```python
import typing
from pathlib import Path

from .. import utils


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: typing.Optional[Path] = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Iowa.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the path to the final CSV
    output_csv = data_dir / "xx.csv"

    ## Do your stuf here

    # Return the path to the final CSV
    return output_csv


if __name__ == "__main__":
    scrape()
```
