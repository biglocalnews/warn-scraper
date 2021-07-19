# America's Job Center

- [Overview](#overview)
- [Scraping strategy](#scraping-strategy)
- [Data quality checks](#data-quality-checks)
- [Alternative scraping strategy](#alternative-scraping-strategy)

## Overview

America's Job Center is a workforce and employment platform used by a
handful of states to post their WARN layoff notices.

The sites have varying names and URLs, but the underlying platform is
identical.

We scrape the below states from Job Center sites:

* [Arizona](az.md)
* [Delaware](de.md)
* [Kansas](ks.md)
* [Maine](me.md)
* [Oklahoma](ok.md)
* [Vermont](vt.md)

State-specific details such as links to state sites can be found in
the pages linked above.

Below are details on the scraping strategy we apply in these states,
as well as ideas for [data quality checks](#data-quality-checks) and an
[alternative scraping strategy](#alternative-scraping-strategy).

## Scraping strategy

We apply a date-based scraping strategy for all Job Center sites.

On the initial scrape, we start with the current year and scrape all years back to the earliest year of data available.
On subsequent runs, we always perform a fresh scrape of the current and prior year, to ensure we capture potential
data updates to recently filed records.

Data for years farther back in time are collected from cached pages rather than scraped anew,
in order to optimize the speed of scrapers and be good Internet citizens. :smiley:

Our date-based approach uses a so-called "stop year" that is hard-coded in our scrapers and
is based on a review of each state's data.

If a state adds more historical data -- i.e. years earlier than our "stop year" -- our current approach would not capture it.

Additionally, in their current form, the scrapers will *not* pick up records that are missing a `Notice Date`.
In practice, this does not appear to be a widespread issue for the states mentioned above, but it does happen.

For example, Kansas had a [single record](https://www.kansasworks.com/search/warn_lookups/64) without a `Notice Date`
(as of this writing). To pinpoint records missing a `Notice Date`, you can perform a
search **without start and end dates** and sort by the `Notice Date` field to view all historical records.

For example, here is the query for Kansas:

> https://www.kansasworks.com/search/warn_lookups?commit=Search&page=1&q%5Bemployer_name_cont%5D=&q%5Bmain_contact_contact_info_addresses_full_location_city_matches%5D=&q%5Bnotice_eq%5D=true&q%5Bnotice_on_gteq%5D=&q%5Bnotice_on_lteq%5D=&q%5Bs%5D=notice_on+desc&q%5Bservice_delivery_area_id_eq%5D=&q%5Bzipcode_code_start%5D=&utf8=%E2%9C%93

One final issue with date-based scraping is that certain records are listed on multiple pages of search results. We apply a deduplication
step at the tail end of the scraping process to address the issue.

Some basic [data quality checks](#data-quality-checks) should allow us to address the `Notice Date` issue. We've also outlined an [alternative scraping strategy](#alternative-scraping-strategy) that might allow us to dynamically capture new historical data (i.e. address the "stop year" issue).

## Data quality checks

Automated data quality scripts should check for records missing the `Notice Date` value as well as for new "stop years"
(i.e. historical data that has been added farther back in time than the year we previously researched and hard-coded).

For missing `Notice Date` values, we should ask the data maintainers to fix these records
at the source. If necessary, we should file a public records request for the layoff notice
and correct the data on our end.

## Alternative scraping strategy

A fully automated scraping strategy could entail scraping backwards in time until we no longer get any search results.
This risks possibly missing "gap" years between the current and start year (and would require special handling
early in a new year). We could address these issues by applying logic that aborts the scrape once multiple consecutive years
with no search results are encountered.

This could free us from having to perform manual research for the earliest year of data available for a state.
It could also make it easier for us to determine if a new year of historical data has been added, and to integrate
the new data in an automated fashion.
