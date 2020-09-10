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
