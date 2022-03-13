from datetime import datetime
from pathlib import Path

from spatula import CSS, HtmlListPage, ListPage, NullSource, SkipItem

from .. import utils
from ..cache import CachedURL

__authors__ = ["chriszs"]
__tags__ = ["html"]


class YearList(ListPage):
    """The list of years to scrape."""

    def __init__(self, *, start, end=None, **kwargs):
        """Initialize a new instance."""
        super().__init__(None, **kwargs)
        self.start = start
        self.end = end or datetime.now().year

    @property
    def years(self):
        """Get the list of years to scrape."""
        return reversed(range(self.start, self.end + 1))

    def process_page(self):
        """Process the page."""
        for year in self.years:
            source = CachedURL(
                f"https://www.dol.state.ga.us/public/es/warn/searchwarns/list?geoArea=9&year={year}&step=search"
            )
            source.cache_dir = self.source.cache_dir
            yield NoticeList(source=source)


class HtmlTableRow:
    """A row in a table."""

    def __init__(self, item):
        """Initialize a new instance."""
        self.item = item

    def is_header(self):
        """Test whether the row is a header."""
        return self.item[0].tag == "th"

    def get_text(self):
        """Get the text of the row."""
        return tuple(utils.clean_text(cell.text_content()) for cell in self.item)


class HmlTable(HtmlListPage):
    """A table of HTML elements."""

    selector = CSS("table tr")

    def process_item(self, item):
        """Process an item."""
        row = HtmlTableRow(item)

        # Skip the header row, saving headers as property
        if row.is_header():
            self.headers = row
            raise SkipItem("headers")

        return dict(zip(self.headers.get_text(), row.get_text()))


class NoticeList(HmlTable):
    """The list of notices for a given year."""

    selector = CSS("#emplrList tr")


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
    years = YearList(start=2002, source=source)
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
