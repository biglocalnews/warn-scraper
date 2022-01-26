import logging
import shutil
from importlib import import_module
from pathlib import Path

from . import utils

logger = logging.getLogger(__name__)


class Runner:
    """High-level interface for scraping state data.

    Provides methods for:
     - directory setup
     - scraping a state
     - deleting files from prior runs

    The cache_dir and output_dir arguments can specify any
    location, but it's not a bad idea to have them as sibling directories:

        /tmp/WARN/working # ETL files
        /tmp/WARN/exports # Final, polished data e.g CSVs for analysis

    Args:
        cache_dir (str): Path to store intermediate files used in ETL.
        data_dir (str): Path where final output files are saved.
    """

    def __init__(
        self,
        data_dir: Path = utils.WARN_DATA_DIR,
        cache_dir: Path = utils.WARN_CACHE_DIR,
    ):
        """Initialize a new instance."""
        self.data_dir = data_dir
        self.cache_dir = cache_dir

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
        """Delete the files in the output directories."""
        logger.debug(f"Deleting files in {self.data_dir}")
        shutil.rmtree(self.data_dir, ignore_errors=True)
        logger.debug(f"Deleting files in {self.cache_dir}")
        shutil.rmtree(self.cache_dir, ignore_errors=True)
