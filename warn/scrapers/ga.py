from datetime import datetime
from pathlib import Path

import requests
import scrapelib
from spatula import CSS, URL, HtmlListPage, ListPage, NullSource, SkipItem

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html"]


class NoticeListSource(URL):
    """The source for the list of notices.

    Args:
        year (int): The year to get the list for.

    Returns:
        ListPage: The list of notices.
    """

    def __init__(
        self,
        year: int,
        area: int = 9,
        base_url: str = "https://www.dol.state.ga.us/public/es/warn/searchwarns/list",
    ) -> None:
        """Initialize the source. Forms a URL from the provided year.

        Args:
            year (int): The year to get the list for.
            area (int): The area to get the list for. Defaults to 9 (statewide).
            base_url (str): The base URL to use.
        """
        self.year = year
        self.area = area
        self.base_url = base_url
        url = f"{self.base_url}?geoArea={self.area}&year={self.year}&step=search"
        super().__init__(url)

    def get_response(self, scraper: scrapelib.Scraper) -> requests.models.Response:
        """Get the response from the source, then writes it to a cache.

        Args:
            scraper (scrapelib.Scraper): The scraper to use.

        Returns:
            requests.models.Response: The response from the source.
        """
        response = scraper.get(self.url)

        # Write the response to the cache
        cache_key = f"ga/{self.year}.html"
        html = response.text
        cache = Cache()
        cache.write(cache_key, html)

        return response


class YearList(ListPage):
    """The list of years to scrape."""

    source = NullSource()

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
            source = NoticeListSource(year)
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
    years = YearList()
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
