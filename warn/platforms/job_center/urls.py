import urllib.parse

class urls:

    @classmethod
    def parse_url_query(cls, url):
        return urllib.parse.parse_qs(url)

    @classmethod
    def page_num_from_url(cls, url):
        queries = cls.parse_url_query(url)
        return int(queries['page'][0]) # it's a one-element array
