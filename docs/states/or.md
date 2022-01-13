# Oregon

- [Home page](https://ccwd.hecc.oregon.gov/Layoff/WARN)
- [Excel/PDF Download](https://www.azjobconnection.gov/search/warn_lookups/new)

- Webmaster [contact email](Kathy.Wilcox@HECC.Oregon.gov) (subject: Rapid Response Tracking System Question)

### July 13, 2021
Sent email to kathy. She responded the next day with this Excel file going all the way back to 1980. We'll keep this somewhere with other historical files to mitigate the scraping load. Scraping strategy for oregon TBD. [OR WARNList July 2021.xlsx](https://github.com/biglocalnews/WARN/files/6819514/OR.WARNList.July.2021.xlsx)


## Scraping strategy
The site also offers downloadable Excel files, which we can likely scrape using session-based requests. This could dramatically simplify and speed up the scrape. However, there are some differences between these data sources that we need to investigate.

The HTML listings do not contain all the fields contained in the Excel downloads. Further, the HTML tables appear to be less up-to-date than the Excel files, and there are discrepancies in the records between these sources.

The HTML listings go back to the mid-90s in terms of coverage, whereas the Excel file only goes back to around 2011.

We should call the OR folks who manage the data to determine:

1. which is the more accurate source for current and recent data
2. if the older historical data can be obtained in a machine-readable format without having to bother with the web scrape
