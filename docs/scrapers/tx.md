# Texas

URL: https://www.twc.texas.gov/businesses/worker-adjustment-and-retraining-notification-warn-notices#warnNotices
"To access older WARN notices or if you have any questions regarding WARN notices, contact TWC at warn.list@twc.texas.gov."

### 1/5/22
Just want to document here that TX is an edge-case scraper, meaning that it has a hybrid strategy of both scraping the website and downloading a historical document, merging the two data. We've hosted the document at https://storage.googleapis.com/bln-data-public/warn-layoffs/tx_historical.xlsx 

### 8/19/21
**Cody:** "Hi Francisco,
Forgive me for my extreme nitpicking, I just want to make extra sure that we are sharing the best source for Texas' WARN data.I am aware of the additional columns, but I noticed some rows in the historical data that aren't present in the 2019 or 2018 data. For a specific example, by manual searching I found the companies "Robert Allen Duralee Group", "Allgoods", and "NTT data" each have several WARNs of notification date 2019 in the historical data, yet aren't present in 2018 or 2019 xlsx files.Can you confirm that you notice these companies aren't present in the public-facing data as well?(I am noticing that for each of these instances, the amount of layoffs were less than 100, and I am wondering if this could be the reason why.)
Thanks for your patience,"

**Francisco:** "There could be a variety of reasons that a WARN notices you mentioned might have appeared in the file we sent you but is not currently on the WARN list on TWC’s website. Below is information that may help you.

https://twc.texas.gov/businesses/worker-adjustment-and-retraining-notification-warn-notices

https://www.doleta.gov/layoff/warn/
"

So it seems like our guess was correct, that the xtra data included in the historical is just not counted in WARN. I am glad we have the extra rows because this data is useful regardless.


### 8/18/21

Noticed historical data seemed more comprehensive than yearly data for 2019 (see WARN/#227). Sent an email bringing to their attention & asking which is the best source of the WARN data. 

"Thanks so much for this data. I noticed something interesting that I thought you might like to be aware of. After looking at the differences between the WARN historical file you provided and the 2019 data available on the public-facing website, I noticed some interesting discrepancies: https://www.diffchecker.com/LBUWndL9I was surprised to find that the historical data includes about 12 additional rows.I think this trend might extend to other years as well. I am wondering if you all are aware of this, and if so, whether the historical data or the data on the website would be a more accurate source for Texas' WARN information."


### 8/16/2021

Received a reply from TX from cisco.gamez@twc.texas.gov, with the following .xlsx file. 

[Warns 01-01-89-09-30-19.xlsx](https://github.com/biglocalnews/WARN/files/6994307/Warns.01-01-89-09-30-19.xlsx)

This file seems to overlap quite a bit with our website scraper, maybe the website scraper can just scrape from 2020 onwards?


### 8/13/21

Sent an email to the provided email address requesting WARN from prior years. Received an email back from cisco.gamez@twc.state.tx.us with the historical WARN data. He also CC'd "Hession,Margaret" <margaret.hession@twc.state.tx.us> and 
"Bernsen,James" <james.bernsen@twc.state.tx.us>
