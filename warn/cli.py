import argparse
import logging
import os
import traceback

from importlib import import_module
from pathlib import Path

from warn import Runner


USER_HOME = os.path.expanduser('~')
DEFAULT_HOME = str(Path(USER_HOME, '.warn-scraper'))
ETL_DIR = os.environ.get('WARN_ETL_DIR', DEFAULT_HOME)
PROCESS_DIR = str(Path(ETL_DIR, 'cache'))
WARN_DATA_PATH = str(Path(ETL_DIR, 'exports'))
WARN_LOG_PATH = str(Path(ETL_DIR, 'logs'))


# Set higher log-level on third-party libs that use DEBUG logging,
# In order to limit debug logging to our library
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('pdfminer').setLevel(logging.WARNING)

def main(args=None):
  log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--output-dir',
      help='Directory where final outputs will be written',
      action='store',
      type=str,
      default=WARN_DATA_PATH
  )
  parser.add_argument(
      '--cache-dir',
      help='Directory where intermediate ETL files should we written',
      action='store',
      default=PROCESS_DIR
  )
  parser.add_argument('--upload', '-u', help='Upload generated files to BLN platform project', action='store_true')
  parser.add_argument('--delete', '-d', help='Delete files from prior scrape at start of new scraper run', action='store_true')
  parser.add_argument('--states', '-s', required=True, help='One or more state postals', nargs='+', action='store')
  parser.add_argument('--log-level', '-l', default='INFO', help='Set the logging level', choices=log_levels)
  # TODO: parser.add_argument('--all', '-a',action='store_true', help='Run all scrapers')

  args = parser.parse_args()
  # Logging config
  logging.basicConfig(
      level=args.log_level,
      format='%(asctime)s - %(name)s - %(message)s'
  )
  logger = logging.getLogger(__name__)
  states = args.states
  output_dir = args.output_dir
  cache_dir = args.cache_dir
  _create_log_dir(WARN_LOG_PATH)
  runner = Runner(cache_dir, output_dir)
  runner.setup()
  succeeded = []
  failed = []
  if args.delete:
    logger.info("Deleting files generated from previous scraper run.")
    runner.delete()
  for state in args.states:
    try:
      runner.scrape(state)
      succeeded.append(state)
    except Exception as e:
      traceback_str = traceback.format_exc()
      state_logfile = Path(WARN_LOG_PATH, f"{state.lower()}_err.log")
      _log_traceback(state_logfile, traceback_str)
      msg = f'ERROR: {state} scraper. See traceback in {state_logfile}'
      logger.error(msg)
      failed.append(state)
  if args.upload:
    try:
      project_id = os.environ['WARN_PROJECT_ID']
      runner.upload(project_id)
    except KeyError:
      msg = ("ERROR: No upload performed. You must set the BLN_API_KEY "
             "and WARN_PROJECT_ID env vars to upload files.")
      logger.error(msg)
  _log_final_status(succeeded, failed, logger)

def _create_log_dir(log_dir):
  return Path(log_dir).mkdir(parents=True, exist_ok=True)

def _log_final_msg(state_list, action, logger):
  msg_base = '{} scraper(s) {}: {}'
  cnt = len(state_list)
  states = ', '.join(state_list)
  msg = msg_base.format(cnt, action, states)
  logger.info(msg)

def _log_final_status(succeeded, failed, logger):
  if succeeded:
    _log_final_msg(succeeded, 'ran successfully', logger)
  if failed:
    _log_final_msg(failed, 'failed to run', logger)

def _log_traceback(logfile, traceback):
  "Write tracebacks to separate state-specific error logs"
  with open(logfile, 'w') as out:
    out.write(traceback)


if __name__ == '__main__':
  main()
