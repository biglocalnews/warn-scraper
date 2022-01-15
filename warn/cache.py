import os
from pathlib import Path
from os.path import join, expanduser


class Cache:
    """
    Basic interface to save files to and fetch from cache.

    By default this will be: ~/.warn-scraper/cache

    With this directory, you can use partial paths to save or fetch
    file contents. State-specific files should generally be stored in a
    folder using the state's two-letter postal code.

    Usage:
        # Say we scraped the first of many pages for 2021 for Florida
        html = '<html><h1>Blob of HTML</h1></hmtl>'
        cache = Cache()
        cache.write('fl/2021_page_1.html', html)

        # To subsequently retrieve pages in cache (e.g. to read and parse)
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
        with open(path, "r", newline="") as infile:
            return infile.read()

    def write(self, name, content):
        """Save file contents to cache.

        Typically, this should be a state-specific directory
        inside the cache/ folder. For example:

            $HOME/.warn-scraper/cache

        Usage:

            Provide file contents and the partial name for (relative to cache directory)
            where file should written. The partial file path can include additional
            directories (e.g. 'fl/2021_page_1.html'), which will be created if they
            don't exist.

        Args:
            name (str): Partial name, relative to cache dir, where content should be saved.
            content (str): Any string content to save to file.
        """
        out = Path(self.path, name)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="") as fh:
            fh.write(content)
        return str(out)

    def files(self, subdir=".", glob_pattern="*"):
        """
        Retrieve all files and folders in a subdir relative to cache dir.

        Usage:
            Given a cache dir such as $HOME/.warn-scraper/cache,
            you can:

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
