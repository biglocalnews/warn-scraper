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
* [Oklahoma](ok.md)

State-specific details such as links to state sites can be found in
the pages linked above.

Below are details on the scraping strategy we apply in these states,
as well as ideas for data quality checks and alternative scraping
strategies.

## Scraping strategy

We apply a date-based scraping strategy for all Job Center sites.

On the initial scrape, we start with the current year and scrape all years back to the earliest year of data available.

On subsequent runs, we always perform a fresh scrape of the current and prior year, to ensure we capture potential
data updates to recently filed records.


Data for years farther back in time are collected from cached pages rather than scraped anew.

Our date-based approach uses a so-called "stop year" that is hard-coded in our scrapers and
is based on a review of each state's data.

If a state adds more historical data, our current approach would not capture it.

Additionally, in their current form, the scrapers will *not* pick up records that are missing a Notified Date.
In practice, this does not appear to be a widespread issue for the states mentioned above, but it does happen.

For example, Kansas had a [single record](https://www.kansasworks.com/search/warn_lookups/64) without a Notified Date
as of this writing. To pinpoint records missing Notification Dates, you can perform a
search **without start and end dates** and sort by the date field to view all historical records.

For example, here is the query for Kansas:

> https://www.kansasworks.com/search/warn_lookups?commit=Search&page=1&q%5Bemployer_name_cont%5D=&q%5Bmain_contact_contact_info_addresses_full_location_city_matches%5D=&q%5Bnotice_eq%5D=true&q%5Bnotice_on_gteq%5D=&q%5Bnotice_on_lteq%5D=&q%5Bs%5D=notice_on+desc&q%5Bservice_delivery_area_id_eq%5D=&q%5Bzipcode_code_start%5D=&utf8=%E2%9C%93

See below for ideas on dealing with the missing Notified Date issues and an alternative scraping strategy that might
enable us to capture newly added historical data.

## Data quality checks

Automated data quality scripts should check for records missing the Notified Date value as well as for new "stop" years
(i.e. historical data that has been added farther back in time than the year we previously researched and hard-coded).

In the case of missing Notified Dates, we should ask the data maintainers to fix these records
at the source. If necessary, we should file public records requests for the layoff notice
and correct the data on our end.

## Alternative scraping strategy

A fully automated scraping strategy would entail scraping backwards in time until we no longer get any search results.
This risks possibly missing "gap" years in between the most recent year and start year, although we
could mitigate this risk by applying logic that aborts the scrape once multiple consecutive years
with no search results are encountered.

This could free us from having to perform manual research for the earliest year of data available for a state.
It could also make it easier for us to determine if a new year of historical data has been added, and to integrate
data in automated fashion.
