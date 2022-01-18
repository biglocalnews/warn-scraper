import logging
import traceback
from pathlib import Path

import click

from . import Runner
from . import utils


@click.command()
@click.argument("states", nargs=-1)
@click.option(
    "--data-dir",
    default=utils.WARN_DATA_DIR,
    type=click.Path(exists=True),
    help="The Path were the results will be saved",
)
@click.option(
    "--cache-dir",
    default=utils.WARN_CACHE_DIR,
    type=click.Path(exists=True),
    help="The Path where results can be cached",
)
@click.option(
    "--delete/--no-delete",
    default=False,
    help="Delete generated files from the cache",
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(
        ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), case_sensitive=False
    ),
    help="Set the logging level",
)
def main(
    states: list,
    data_dir: Path,
    cache_dir: Path,
    delete: bool,
    log_level: str,
):
    """
    Command-line interface for downloading WARN Act notices.

    STATES -- a list of one or more state postal codes to scrape. Pass `all` to scrape all supported states.
    """
    # Set higher log-level on third-party libs that use DEBUG logging,
    # In order to limit debug logging to our library
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("pdfminer").setLevel(logging.WARNING)

    # Local logging config
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(message)s")
    logger = logging.getLogger(__name__)
    utils.WARN_LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Runner config
    runner = Runner(data_dir, cache_dir)
    runner.setup()

    # Delete files, if asked
    if delete:
        logger.info("Deleting files generated from previous scraper run.")
        runner.delete()

    # Track how we do
    succeeded = []
    failed = []

    # If the user has asked for all states, give it to 'em
    if "all" in states:
        states = utils.get_all_states()

    # Loop through the states
    for state in states:
        try:
            # Try running the scraper
            runner.scrape(state)

            # Tally if it succeeds
            succeeded.append(state)
        except Exception:
            # If it fails, log out the traceback
            log_path = utils.WARN_LOG_DIR / f"{state.lower()}_err.log"
            with open(log_path, "w") as f:
                f.write(traceback.format_exc())

            # And spit an error to the terminal
            msg = f"ERROR: {state} scraper. See traceback in {log_path}"
            logger.error(msg)

            # Then add the state to our tally of failures
            failed.append(state)

    # Log out our final status
    if succeeded:
        logger.info(f"{len(succeeded)} ran successfully: {', '.join(succeeded)}")
    if failed:
        logger.info(f"{len(failed)} failed to run: {', '.join(failed)}")


if __name__ == "__main__":
    main()
