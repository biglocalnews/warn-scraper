# Sources

There are currently scrapers for {{ haves|length }} of America's {{ targets|length }} states and territories.

| State | Scraper | Docs |
|:--- |:--- |:---:|
{% for obj in haves -%}
|{{ obj.name }}|[{{ obj.abbr|lower }}.py](https://github.com/biglocalnews/warn-scraper/blob/main/warn/scrapers/{{ obj.abbr|lower }}.py)|{% if obj.has_docs %}[📃](scrapers/{{ obj.abbr|lower }}.md){% endif %}|
{% endfor %}

## To do

These {{ have_nots|length }} areas need a scraper:

{% for obj in have_nots -%}
* {{ obj.name }}
{% endfor %}
