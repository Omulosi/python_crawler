from csv import DictWriter
import requests

PAGE_SIZE = 1000

template_url = 'http://example.webscraping.com/places/ajax/search.json?&search_term=.&page_size={}&page=0'

resp = requests.get(template_url.format(PAGE_SIZE))
data = resp.json()
records = data.get('records')
print(records)

with open('../data/nations.csv', 'w') as countries_file:
    writer = DictWriter(countries_file, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
