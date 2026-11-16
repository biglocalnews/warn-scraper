---
orphan: true
---

# North Carolina

The source is the "Workforce WARN Summary List" for the current year, an HTML table published by the [N.C. Department of Commerce](https://www.commerce.nc.gov/data-tools-reports/labor-market-data-tools/workforce-warn-reports).

- One page per calendar year, at `.../workforce-warn-reports/report-workforce-warn-summary-list-YYYY`. The scraper requests the current year's page once and reads the table from the HTML.
- The page also links an "Export Table Data" CSV with the same rows. Its file name is dated and changes with every update, so the scraper reads the table instead.
- Earlier years are published only as PDFs and are not scraped.
- Each row is one location. A notice covering several sites can appear as several rows that share a `Warn Number`, so that column is not unique (60 numbers across the 71 rows of 2026).

### 11/16/2026
Scraper added. The 2026 list had 71 rows.
