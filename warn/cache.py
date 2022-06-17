import csv
import logging
import os
import typing
from os.path import expanduser, join
from pathlib import Path

from .utils import get_url

logger = logging.getLogger(__name__)


class Cache:
    """Basic interface to save files to and fetch from cache.

    By default this will be: ~/.warn-scraper/cache

    With this directory, you can use partial paths to save or fetch
    file contents. State-specific files should generally be stored in a
    folder using the state's two-letter postal code.

    Example:
        Saving HTML to the cache::

            html = '<html><h1>Blob of HTML</h1></hmtl>'
            cache = Cache()
            cache.write('fl/2021_page_1.html', html)

        Retrieving pages from the cache::

            cache.files('fl')

    Args:
        path (str): Full path to cache directory. Defaults to WARN_ETL_DIR
            or, if env var not specified, $HOME/.warn-scraper/cache
    """

    def __init__(self, path=None):
        """Initialize a new instance."""
        self.root_dir = self._path_from_env or self._path_default
        self.path = path or str(Path(self.root_dir, "cache"))

    def exists(self, name):
        """Test whether the provided file path exists."""
        return Path(self.path, name).exists()

    def read(self, name):
        """Read text file from cache.

        Args:
            name (str): Partial name, relative to cache dir (eg. 'fl/2021_page_1.html')

        Returns:
            File content as string or error if file doesn't
        """
        path = Path(self.path, name)
        logger.debug(f"Reading from cache {path}")
        with open(path, newline="") as infile:
            return infile.read()

    def read_csv(self, name):
        """Read csv file from cache.

        Args:
            name (str): Partial name, relative to cache dir (eg. 'fl/2021_page_1.html')

        Returns:
            list of rows
        """
        path = Path(self.path, name)
        logger.debug(f"Reading CSV from cache {path}")
        with open(path) as fh:
            return list(csv.reader(fh))

    def download(
        self, name: str, url: str, encoding: typing.Optional[str] = None, **kwargs
    ) -> Path:
        """
        Download the provided URL and save it in the cache.

        Args:
            name (str): The path where the file will be saved. Can be a simple string like "ia/data.xlsx"
            url (str): The URL to download
            encoding (str): The encoding of the response. Optional.
            **kwargs: Additional arguments to pass to requests.get()

        Returns: The Path where the file was saved
        """
        # Request the URL
        logger.debug(f"Downloading {url}")
        with get_url(url, stream=True, **kwargs) as r:
            # If there's no encoding, set it
            if encoding:
                r.encoding = encoding
            elif r.encoding is None:
                r.encoding = "utf-8"

            # Open the local Path
            out_path = Path(self.path, name)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Writing to {out_path}")

            # Write out the file in little chunks
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Return the path
        return out_path

    def write(self, name, content):
        """Save file contents to cache.

        Typically, this should be a state-specific directory
        inside the cache folder.

        For example: ::

            $HOME/.warn-scraper/cache

        Provide file contents and the partial name for (relative to cache directory)
        where file should written. The partial file path can include additional
        directories (e.g. 'fl/2021_page_1.html'), which will be created if they
        don't exist.

        Example: ::

            cache.write("fl/page.html", html)

        Args:
            name (str): Partial name, relative to cache dir, where content should be saved.
            content (str): Any string content to save to file.
        """
        out = Path(self.path, name)
        out.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Writing to cache {out}")
        with open(out, "w", newline="") as fh:
            fh.write(content)
        return str(out)

    def files(self, subdir=".", glob_pattern="*"):
        """
        Retrieve all files and folders in a subdir relative to cache dir.

        Examples:
            Given a cache dir such as $HOME/.warn-scraper/cache,
            you can: ::

                # Get all files and dirs in cache dir
                Cache().files()

                # Get files in specific subdir
                Cache().files('fl/')

                # Get all files of a specific type in a subdir
                Cache().files(subdir='fl/', glob_pattern='*.html')

        Args:
            subdir (str): Subdir inside cache to glob
            glob_pattern (str): Glob pattern. Defaults to all files in specified subdir ('*')
        """
        _dir = Path(self.path).joinpath(subdir)
        return [str(p) for p in _dir.glob(glob_pattern)]

    @property
    def _path_from_env(self):
        """Get the path where files will be saved."""
        return os.environ.get("WARN_ETL_DIR")

    @property
    def _path_default(self):
        """Get the default filesystem location of the cache."""
        return join(expanduser("~"), ".warn-scraper")
