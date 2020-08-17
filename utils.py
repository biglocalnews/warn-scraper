from datetime import datetime

def relative_year(month, day):
    """Given a month and day,
    determine the correct year on
    New Year's Day
    """
    t = today()
    # If incoming date is Jan 1st
    if month == 1 and day == 1:
        # and current UTC is Dec 31st,
        # then increment the current year
        if t.month == 12 and t.day == 31:
            return t.year + 1
    return t.year

def today():
    return datetime.utcnow()

def utc_now_timestamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%MZ")