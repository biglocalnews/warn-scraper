# Missouri

- [Homepage](https://jobs.mo.gov/)
- Sample data links
  - https://jobs.mo.gov/warn2021
  - https://jobs.mo.gov/content/2020-missouri-warn-notices
  - https://jobs.mo.gov/warn2019
- [Contact for data inquiries](https://dhewd.mo.gov/contactus.php)

### Jul 2nd, 2021

Notes about dedupe/data cleaning strategy currently applied to Missouri:
- `.warn-scraper/exports/mo.csv`
  - 2020 data scraped from [the 2019 page](https://jobs.mo.gov/warn2019) is not included in the output because the state agency has indicated the need of an audit of the overlapping data.
  - a pandas dedupe function is applied to the output data to get rid of any complete duplication, but highly similar entries (usually due to multiple locations of the same company and possibly include over-counting of the total number of employees affected) need further examination at a case by case level.
- `.warn-scraper/cache/mo_raw.csv`
  - this csv simply contains all data records scraped from the website without data validation mentioned above.

### Jul 1st, 2021

Response from MO Department of Higher Education and Workforce Devlopment about the data issues:
![image](https://user-images.githubusercontent.com/56002814/124181019-fc64cc00-da82-11eb-87ed-d3c6cd2e3021.png)


### Jun 29th, 2021 

The following are some specific issues with this data that needs further processing and phone calls:
- year 2015-2019 data is in fiscal year, but year 2020 and 2021 data is in calendar year. This produced some number of duplicate data entries between 2019 and 2020 data page. Some of these duplicate entries have minor differences in number affected. This issue requires us to inquiry about the difference between the 2020 and 2019 data page as well as how updated date works for different companies (some companies have multiple entries with same date but different numbers). Currently, I am waiting for a response from the state agency.
- year 2017, 2016, 2015, has different date string format from the rest
- 2021 has a new industry column
