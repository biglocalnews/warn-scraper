import glob
import logging
import os

from importlib import import_module
from pathlib import Path

from bln_etl.api import Project

logger = logging.getLogger(__name__)


class Runner:
    """High-level interface for scraping state data

    Provides methods for:
     - directory setup
     - scraping a state
     - uploading files
     - deleting files from prior runs

    The working_dir and output_dir arguments can specify any
    location, but it's not a bad idea to have them as sibling directories:

        /tmp/WARN/working # ETL fiiles
        /tmp/WARN/exports # Final, polished data e.g CSVs for analysis

    Args:
        working_dir (str): Path to store intermediate files used in ETL.
        output_dir (str): Path where final output files are saved.

    """

    def __init__(self, working_dir, output_dir):
        self.working_dir = working_dir
        self.output_dir = output_dir

    def setup(self):
        logger.info("Creating necessary dirs")
        for d in [self.working_dir, self.output_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

    def scrape(self, state):
        state_mod = import_module('warn.scrapers.{}'.format(state.strip().lower()))
        logger.info(f"Scraping {state}")
        output_csv = state_mod.scrape(self.output_dir, self.working_dir)
        logger.info(f"Generated {output_csv}")

    def upload(self, project_id, api_token=None):
        logger.info(f"Uploading files in {self.output_dir}")
        project = Project.get(project_id, api_token=api_token)
        project.upload_files(self._output_dir_files)

    def delete(self):
        logger.info(f"Deleting files in {self.output_dir}")
        for f in self._output_dir_files:
            Path(f).unlink()

    @property
    def _output_dir_files(self):
        return [str(f) for f in Path(self.output_dir).glob('*')]
