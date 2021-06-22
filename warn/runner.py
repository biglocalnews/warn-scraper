import logging
import re
import os

from importlib import import_module
from pathlib import Path


try:
    LOGDIR = os.environ['WARN_LOG_DIR']
except KeyError:
    LOGDIR = '/tmp/warn/logs'
    Path(LOGDIR).mkdir(parents=True, exist_ok=True)

log_file = os.path.join(LOGDIR, 'warn.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-12s - %(message)s',
    datefmt='%m-%d %H:%M',
    filename=log_file,
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)



class Runner:

    def __init__(self, working_dir, output_dir):
        self.working_dir = working_dir
        self.output_dir = output_dir

    def setup(self):
        for d in [self.working_dir, self.output_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

    def scrape(self, state):
        state_mod = import_module('warn.scrapers.{}'.format(state.strip().lower()))
        status_msg = 'No errors in scraping.'
        return state_mod.scrape(self.output_dir)
        #TODO:
        #logged_info = send_query()
        #data_dir = os.environ['WARN_DATA_PATH']
        #TODO: Below removes previously created files at end of run
        #move_data(data_dir)

    def upload(self, file_path):
        #TODO: use bln-etl
        logger.info(f"Uploading to platform: {file_path}")

    def cleanup(self):
        #TODO: Clobber pre-existing files
        pass
