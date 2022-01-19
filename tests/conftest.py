import shutil
from pathlib import Path

import pytest

# NOTE: To check if vcrpy/pytest-vcr
# is using cassettes as opposed to making
# live web requests, uncomment below
# and pass pytest caplog fixture to
# a test function. More details here:
#    https://vcrpy.readthedocs.io/en/latest/debugging.html
# import vcr
# import logging
# Initialize logging in order see output from vcrpy
# logging.basicConfig()
# vcr_log = logging.getLogger("vcr")
# vcr_log.setLevel(logging.INFO)


@pytest.fixture
def warn_scraper_dir(tmp_path):
    """Set scraper directory."""
    return str(tmp_path.joinpath("warn-scraper"))


@pytest.fixture
def cache_dir(warn_scraper_dir):
    """Set scraper directory."""
    return str(Path(warn_scraper_dir).joinpath("cache"))


@pytest.fixture
def create_scraper_dir(warn_scraper_dir):
    """Create scraper directory."""
    Path(warn_scraper_dir).mkdir(parents=True, exist_ok=True)


@pytest.fixture
def create_cache_dir(cache_dir):
    """Create cache directory."""
    Path(cache_dir).mkdir(parents=True, exist_ok=True)


@pytest.fixture
def copy_html_to_cache(cache_dir):
    """Copy HTML content to cache directory."""
    fl_dir = Path(cache_dir).joinpath("fl")
    fl_dir.mkdir(parents=True, exist_ok=True)
    for html_fixture in ["2021_page_1.html", "2021_page_2.html"]:
        src = Path(__file__).parent.joinpath("fixtures").joinpath(html_fixture)
        dest = fl_dir.joinpath(html_fixture)
        shutil.copy(src, dest)


@pytest.fixture
def set_etl_dir_env_var(warn_scraper_dir, monkeypatch):
    """Set the environment variable for the output directory."""
    monkeypatch.setenv("WARN_ETL_DIR", warn_scraper_dir)


def read_fixture(file_name):
    """Read in provided fixture."""
    path = str(Path(__file__).parent.joinpath("fixtures").joinpath(file_name))
    return file_contents(path)


def file_contents(pth):
    """Read provided file path."""
    with open(pth, newline="") as f:
        return f.read()


def write_file(pth, contents):
    """Write to provided file path."""
    Path(pth).parent.mkdir(parents=True, exist_ok=True)
    with open(pth, "w", newline="") as f:
        f.write(contents)
