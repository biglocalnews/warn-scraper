import logging

from importlib import import_module
from pathlib import Path

logger = logging.getLogger(__name__)


class Runner:
    """High-level interface for scraping state data.

    Provides methods for:
     - directory setup
     - scraping a state
     - deleting files from prior runs

    The cache_dir and output_dir arguments can specify any
    location, but it's not a bad idea to have them as sibling directories:

        /tmp/WARN/working # ETL fiiles
        /tmp/WARN/exports # Final, polished data e.g CSVs for analysis

    Args:
        cache_dir (str): Path to store intermediate files used in ETL.
        data_dir (str): Path where final output files are saved.
    """

    def __init__(self, data_dir: Path, cache_dir: Path):
        """Initialize a new instance."""
        self.data_dir = data_dir
        self.cache_dir = cache_dir

    def setup(self):
        """Create the necessary directories."""
        for d in [self.cache_dir, self.data_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

    def scrape(self, state):
        """Run the scraper for the provided state."""
        # Get the module
        state = state.strip().lower()
        state_mod = import_module(f"warn.scrapers.{state}")

        # Run the scrape method
        logger.info(f"Scraping {state}")
        data_path = state_mod.scrape(self.data_dir, self.cache_dir)

        # Run the path to the data file
        logger.info(f"Generated {data_path}")
        return data_path

    def delete(self):
        """Delete the files in the output directory."""
        logger.info(f"Deleting files in {self.output_dir}")
        for f in self._output_dir_files:
            Path(f).unlink()

    @property
    def _output_dir_files(self):
        """Get a list of output files."""
        return [str(f) for f in Path(self.output_dir).glob("*")]
