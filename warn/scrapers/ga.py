from datetime import datetime
from pathlib import Path

from spatula import CSS, HtmlListPage, ListPage, NullSource, SkipItem

from .. import utils
from ..cache import CachedURL

__authors__ = ["chriszs"]
__tags__ = ["html"]


class YearList(ListPage):
    """The list of years to scrape."""

    first_year = 2002  # first available year

    @property
    def current_year(self):
        """Get the current year."""
        return datetime.now().year

    @property
    def years(self):
        """Get the list of years to scrape."""
        return reversed(list(range(self.first_year, self.current_year + 1)))

    def process_page(self):
        """Process the page."""
        for year in self.years:
            source = CachedURL(
                f"https://www.dol.state.ga.us/public/es/warn/searchwarns/list?geoArea=9&year={year}&step=search"
            )
            source.cache_dir = self.source.cache_dir
            yield NoticeList(source=source)


class NoticeList(HtmlListPage):
    """The list of notices for a given year."""

    selector = CSS("#emplrList tr")

    def process_item(self, item):
        """Process an item."""
        cells = item.getchildren()
        text = tuple(utils.clean_text(cell.text_content()) for cell in cells)

        # Skip the header row, saving headers as property
        if cells[0].tag == "th":
            self.headers = text
            raise SkipItem("headers")

        return dict(zip(self.headers, text))


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Georgia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Loop through the years and scrape them one by one
    source = NullSource()
    source.cache_dir = cache_dir / "ga"
    years = YearList(source=source)
    rows = tuple(years.do_scrape())
    headers = rows[0].keys()

    # Write out the results
    data_path = data_dir / "ga.csv"
    utils.write_dict_rows_to_csv(
        data_path,
        headers,
        rows,
    )

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
