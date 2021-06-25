import glob
import logging
import os

from importlib import import_module
from pathlib import Path

from bln_etl.api import Project

logger = logging.getLogger(__name__)


class Runner:

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

    def upload(self, project_id):
        logger.info(f"Uploading files in {self.output_dir}")
        project = Project.get(project_id)
        project.upload_files(self._output_dir_files)

    def delete(self):
        logger.info(f"Deleting files in {self.output_dir}")
        for f in self._output_dir_files:
            Path(f).unlink()

    @property
    def _output_dir_files(self):
        return [str(f) for f in Path(self.output_dir).glob('*')]
