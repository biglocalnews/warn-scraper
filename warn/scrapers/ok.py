import logging
from pathlib import Path

import requests

from .. import utils

__authors__ = ["zstumgoren", "Dilcia19", "stucka"]
__tags__ = [""]
__source__ = {
    "name": "Oklahoma Office of Workforces Development",
    "url": "https://www.employoklahoma.gov/Participants/s/warnnotices",
}

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
    use_cache: bool = True,
) -> Path:
    """
    Scrape data from Oklahoma.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)
    use_cache -- a Boolean indicating whether the cache should be used (default True)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "ok.csv"
    # search_url = "https://okjobmatch.com/search/warn_lookups"
    # search_url = "https://www.employoklahoma.gov/Participants/s/warnnotices"
    posturl = "https://www.employoklahoma.gov/Participants/s/sfsites/aura?r=2&aura.ApexAction.execute=6"

    # There are a bunch of hard-coded values in here that seem to work for at least a day.
    # Undetermined:
    # -- Will this continue working in the short- or medium-term?
    # -- What is the signficance of each variable?
    # -- How do we refresh these?

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.employoklahoma.gov/Participants/s/warnnotices",
        "X-SFDC-LDS-Endpoints": "ApexActionController.execute:ConfigurableLoginAndMaintenanceMessages.hasDocument, ApexActionController.execute:ConfigurableLoginAndMaintenanceMessages.checkJobExpiry, ApexActionController.execute:ConfigurableLoginAndMaintenanceMessages.checkResumeExpiry, ApexActionController.execute:ConfigurableLoginAndMaintenanceMessages.checkUIRegistered, ApexActionController.execute:ConfigurableLoginAndMaintenanceMessages.getLoginMaintenanceMessage, ApexActionController.execute:OESC_JS_getWARNLayoffNotices.getListofLayoffAccService",
        "X-SFDC-Page-Scope-Id": "9c659a19-8020-41b0-a81c-36335e22801a",
        "X-SFDC-Request-Id": "16140000007a08bd2f",
        "X-SFDC-Page-Cache": "9439898463d86806",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "X-B3-TraceId": "856a2236ba7d283e",
        "X-B3-SpanId": "b79b2da3a7dc4544",
        "X-B3-Sampled": "0",
        "Origin": "https://www.employoklahoma.gov",
        "Connection": "keep-alive",
        "Cookie": "renderCtx=%7B%22pageId%22%3A%223823bba2-3b00-4db7-aca6-5ca0eb67fc63%22%2C%22schema%22%3A%22Published%22%2C%22viewType%22%3A%22Published%22%2C%22brandingSetId%22%3A%22fa0b6362-0214-44b9-947d-2543eaab22c7%22%2C%22audienceIds%22%3A%22%22%7D; CookieConsentPolicy=0:1; LSKey-c$CookieConsentPolicy=0:1; pctrk=f3070d0c-7078-4062-96bb-de9e82cbb1db",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    payload = "message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22156%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22ConfigurableLoginAndMaintenanceMessages%22%2C%22method%22%3A%22hasDocument%22%2C%22params%22%3A%7B%7D%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%2C%7B%22id%22%3A%22157%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22ConfigurableLoginAndMaintenanceMessages%22%2C%22method%22%3A%22checkJobExpiry%22%2C%22params%22%3A%7B%7D%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%2C%7B%22id%22%3A%22158%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22ConfigurableLoginAndMaintenanceMessages%22%2C%22method%22%3A%22checkResumeExpiry%22%2C%22params%22%3A%7B%7D%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%2C%7B%22id%22%3A%22159%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22ConfigurableLoginAndMaintenanceMessages%22%2C%22method%22%3A%22checkUIRegistered%22%2C%22params%22%3A%7B%7D%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%2C%7B%22id%22%3A%22160%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22ConfigurableLoginAndMaintenanceMessages%22%2C%22method%22%3A%22getLoginMaintenanceMessage%22%2C%22params%22%3A%7B%22displayTo%22%3A%22Job%20Seekers%22%2C%22messageType%22%3A%22Portal%20Login%20Messages%22%7D%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%2C%7B%22id%22%3A%22161%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22OESC_JS_getWARNLayoffNotices%22%2C%22method%22%3A%22getListofLayoffAccService%22%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22eE5UbjZPdVlRT3M0d0xtOXc5MzVOQWg5TGxiTHU3MEQ5RnBMM0VzVXc1cmcxMi42MjkxNDU2LjE2Nzc3MjE2%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%221305_7pTC6grCTP7M16KdvDQ-Xw%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Atrue%7D&aura.pageURI=%2FParticipants%2Fs%2Fwarnnotices&aura.token=null"

    logger.debug(f"Attempting to send hard-coded data to {posturl}")
    r = requests.post(posturl, headers=headers, data=payload)
    rawdata = r.json()

    for entry in rawdata["actions"]:
        if (
            entry["id"] == "161;a"
        ):  # What is this value? Will this change? Also no idea.
            cleanerdata = entry["returnValue"]["returnValue"]
    """
    fields = set()
    for entry in cleanerdata:
        for field in entry:
            fields.add(field)
    {'Id',
     'Launchpad__Layoff_Closure_Type__c',
     'Launchpad__Notice_Date__c',
     'OESC_Employer_City__c',
     'OESC_Employer_Name__c',
     'OESC_Employer_Zip_Code__c',
     'RecordTypeId',
     'Select_Local_Workforce_Board__c'}
    """
    fields = {
        "Id": "id",
        "Launchpad__Layoff_Closure_Type__c": "closure_type",
        "Launchpad__Notice_Date__c": "notice_date",
        "OESC_Employer_City__c": "city",
        "OESC_Employer_Name__c": "company name",
        "OESC_Employer_Zip_Code__c": "zip_code",
        "RecordTypeId": "record_type_id",
        "Select_Local_Workforce_Board__c": "workforce_board",
    }

    masterlist = []
    for entry in cleanerdata:
        line = {}
        for item in fields:
            if item in entry:
                line[fields[item]] = entry[item]
            else:
                line[fields[item]] = None
        masterlist.append(line)

    utils.write_dict_rows_to_csv(output_csv, list(fields.values()), masterlist)
    return output_csv


if __name__ == "__main__":
    scrape()
