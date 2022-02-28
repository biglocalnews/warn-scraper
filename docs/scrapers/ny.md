---
orphan: true
---

# New York

- [Homepage](https://dol.ny.gov/warn-notices)
- To request for full documentation of any notices prior to 2021, email WebHelp@labor.ny.gov
- [Contacts](https://dol.ny.gov/worker-adjustment-and-retraining-notification-warn)
  - NYS WARN Coordinator:	Janet Faraone	(phone: 518-457-1518, email: [Janet.Faraone@labor.ny.gov](Janet.Faraone@labor.ny.gov))

### Jan 5, 2022
We've implemented historical document scraping for NY (issue #136) and removed the old website scraping system while we wait for their website to be upgraded. As mentioned in July, we should implement a system of periodically requesting a historical document from NY. We are hosting this historical document at https://storage.googleapis.com/bln-data-public/warn-layoffs/ny_historical.xlsx .

### Jul 12th, 2021
reaching out to the NYS WARN coordinator was fruitful. the state agency prepared and sent over an excel containing records from 2016 to 2021 within a day upon email request. Here is a snippet of the data:
![image](https://user-images.githubusercontent.com/56002814/125342121-736f4f80-e322-11eb-8c22-b1f22346ded7.png)
The full dataset is currently attached to issue #136, it should be hosted on some platform in the future.
When requesting the data, the state agency asked for a timeframe from which data is needed (i responded with 2016-2021), but it might be possible to request data prior to 2016 as well.
Regarding updating data in the future, the NYS WARN website is undergoing updates, and it should allow scraping in the future. In the meantime, we should periodically request updated data from NYS.

### Jul 6th, 2021
- 2021 data doesn't directly contain # employee affected in the html table on the website, needs to parse the corresponding pdf to obtain the # affected.
- for data prior to 2021, each year is contained in a pdf and doesn't contain # affected, needs to reach out and ask if there is a better form of data/access company specific data.
