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


# These are good to go:

""""

Closure - City: Niles,  County: Berrien, Number Affected: 56
Closure - City: Baldwin, County: Lake, Number Affercted: 107
Closure: City: Detroit, County: Wayne, Number Affected: 145

"""