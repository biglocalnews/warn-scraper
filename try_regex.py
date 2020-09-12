import re

text = 'Closure - City: Niles,  County: Berrien, Number Affected: 56'
# Regex below is tweaked slightly for 'Affercted'
pattern = re.compile("""
    (?P<category>.*) #grabs the type of notice
    \s-\sCit(?:y|ies):?\s #identifies city/cities
    (?P<city>.*)
    ,\sCount(?:y|ies)(?:\sName)?:?\s
    (?P<county>.*)
    ,\s
    (?P<unit>Number\w?|Program\w?)
    \sAffected[:|;|\s]|\sAffercted[:|;|\s]
    (?P<count>.*)
    """, re.VERBOSE)
match = re.search(pattern, text)
category, city, county, unit, count = match.groups()


# Full original regex without comments
"(?P<category>.*)\s-\sCit(?:y|ies):?\s(?P<city>.*),\sCount(?:y|ies)(?:\sName)?:?\s(?P<county>.*),\s(?P<unit>Number\w?|Program\w?)\sAffected[:|;|\s](?P<count>.*)"

# Work in Pythex to tweak the regex.
# Updated version: affercted, and County with extra spaces behind
"(?P<category>.*)\s-\sCit(?:y|ies):?\s(?P<city>.*),(?:\s|\s\S)Coun(?:ty|ies)(?:\sName)?:?\s(?P<county>.*),\s(?P<unit>Number\w?|Program\w?)\sAffe(?:cted|rcted)[:|;|\s](?P<count>.*)"

# Updated Version 2: all above + Closure: instead of Closure - 
"(?P<category>.*)(?:\s-\s|:\s)Cit(?:y|ies):?\s(?P<city>.*),(?:\s|\s\S)Coun(?:ty|ies)(?:\sName)?:?\s(?P<county>.*),\s(?P<unit>Number\w?|Program\w?)\sAffe(?:cted|rcted)[:|;|\s](?P<count>.*)"

# This string is an issue, figure it out later
# Layoff - City: Lansing,  Couny: Ingham, Number Affected: 27




# Rows that are still currently errors

"""

LayOff - City: Ann Arbor, County: Washtenaw,  Number Affected: 79

Closure - City: Sault Saint Marie, County Chippewa, Number of Affected: 47

Layoff - City: Grand Rapids,  County: Kent, Number Affected: 106

Layoff - City:Midland, County: Midland, Number Affected: 100

Layoff - City: Negaunee, Ishpeming, and Palmer; County Name: Marquette, Number Affected: 318

Layoff - City: Flint, Lansing, Mt. Pleasant, Bay City: County: Genesee, Ingham, Bay County, Isabella; Number Affected: 84

Closure - City: Hartland; County: Livingston; Number Affected: 130

Closure -  City: Auburn Hills, County: Oakland, Number Affected: 129

Closure: City: Detroit, County: Wayne, Number Affected: 145

Closure - City: Baldwin, County: Lake, Number Affercted: 107

Layoff - City: Lansing,  Couny: Ingham, Number Affected: 27

Closure - City: Niles,  County: Berrien, Number Affected: 56


Closure - City: Petoskey, County: Emmet
Layoff - City: Traverse City, County: Grand Traverse
Layoff - City: Gaylord, County: Otsego
Total Number Affected: 101

"""


# These are good to go:

""""

Closure - City: Niles,  County: Berrien, Number Affected: 56
Closure - City: Baldwin, County: Lake, Number Affercted: 107
Closure: City: Detroit, County: Wayne, Number Affected: 145

"""


## Mostly working
# (?P<category>.*)(?:\s-|:)(?:\S\s|\s|\S)Cit(?:y|ies):?\s*(?P<city>.*)(?:,|;) #cities
# (?:\s|\S\s|\S|\s\s|\S\S|\S\s\S)Coun(?:ty|ies|y)(?:\sName)?:?\s(?P<county>.*)

# (?:\s*\S*|\S*\s*)


# saved regex, the most recent
# https://regex101.com/r/PgAtOM/1