---
orphan: true
---

# Maryland

- [Homepage](http://www.dllr.state.md.us/employment/warn.shtml)

### Jul 9th
- Updated the scraper to scrape warn notices from each year through links on the homepage. It defaults to scraping the current year, and caches the html of previous years into the cache directory.
- There is a minor bug with scraping 2012 data (somehow scrapes multiple tr's into one list??) Currently implemented a hard-coded fix. This needs further review/debugging.
