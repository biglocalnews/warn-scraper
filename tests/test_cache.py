from pathlib import Path
from unittest.mock import patch

import pytest

from warn.cache import Cache

from .conftest import file_contents


def test_default_cache_dir():
    """Override the output of the expanduser method."""
    to_patch = "warn.cache.expanduser"
    with patch(to_patch) as mock_func:
        mock_func.return_value = "/Users/you"
        cache = Cache()
        assert cache.path == "/Users/you/.warn-scraper/cache"


def test_custom_cache_path(tmpdir):
    """Test if the provided path matches the cache's path."""
    from warn.cache import Cache

    cache = Cache(tmpdir)
    assert tmpdir == cache.path


def test_write(tmpdir):
    """Test writing to the cache."""
    from warn.cache import Cache

    cache = Cache(tmpdir)
    content = "<h1>some content</h1>"
    file_path = "fl/2021_page_1.html"
    outfile = cache.write(file_path, content)
    scrape_dir = tmpdir.join("fl")
    files = [f.basename for f in scrape_dir.listdir()]
    assert "2021_page_1.html" in files
    actual_contents = file_contents(outfile)
    assert actual_contents == content


@pytest.mark.usefixtures("create_cache_dir", "copy_html_to_cache")
def test_files(cache_dir):
    """Test the file fetching function of the cache."""
    from warn.cache import Cache

    cache = Cache(path=cache_dir)
    # Base cache dir only contains fl/ dir
    assert cache.files()[0].endswith("/fl")
    # HTML files are stored in fl/ directory
    actual = [str(p) for p in Path(cache_dir, "fl").glob("*.html")]
    assert cache.files(subdir="fl/") == actual


@pytest.mark.usefixtures("create_cache_dir", "copy_html_to_cache")
def test_exists(cache_dir):
    """Test the exists method of the cache."""
    from warn.cache import Cache

    cache = Cache(path=cache_dir)
    assert cache.exists("fl/2021_page_1.html")


@pytest.mark.usefixtures("create_cache_dir", "copy_html_to_cache")
def test_read(cache_dir):
    """Test reading from the cache."""
    from warn.cache import Cache

    cache = Cache(path=cache_dir)
    html = cache.read("fl/2021_page_1.html").strip()
    assert html == "<html><h1>2021 page 1</h1></html>"
