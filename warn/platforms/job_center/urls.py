import urllib.parse


class urls:
    """Create a URL object."""

    @classmethod
    def parse_url_query(cls, url):
        """Parse the querystring from a URL."""
        return urllib.parse.parse_qs(url)

    @classmethod
    def page_num_from_url(cls, url):
        """Pull page number from URL."""
        queries = cls.parse_url_query(url)
        return int(queries["page"][0])  # it's a one-element array
