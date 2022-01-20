import logging
import re

from warn.cache import Cache as BaseCache

from .urls import urls

logger = logging.getLogger(__name__)


class Cache(BaseCache):
    """A custom cache for Job Center sites."""

    def save(self, url, params, html):
        """Save file to the cache."""
        cache_key = self.key_from_url(url, params)
        self.write(cache_key, html)
        logger.debug(f"Saved to cache: {cache_key}")

    def fetch(self, url, params):
        """Fetch file from the cache."""
        cache_key = self.key_from_url(url, params)
        content = self.read(cache_key)
        logger.debug(f"Fetched from cache: {cache_key}")
        return content

    def key_from_url(self, url, params=None):
        """Convert a URL to a cache key."""
        page_type = (
            "records" if re.search(r"warn_lookups/\d+$", url) else "search_results"
        )
        if page_type == "records":
            record_number = url.rsplit("/")[-1]
            cache_key = f"records/{record_number}.html"
        # Otherwise this is an initial search with params or a downstream page URL
        else:
            start_key = "q[notice_on_gteq]"
            end_key = "q[notice_on_lteq]"
            # For downstream pages, extract start/end dates + page number
            if "page" in url:
                parsed_params = urls.parse_url_query(url)
                page_num = urls.page_num_from_url(url)
                start = parsed_params[start_key][0]
                end = parsed_params[end_key][0]
            # For initial search page, get metadata from params
            else:
                if not params:
                    params = {}
                start = params[start_key]
                end = params[end_key]
                page_num = 1
            cache_key = f"search_results/{start}_{end}_page{page_num}.html"
        return cache_key
