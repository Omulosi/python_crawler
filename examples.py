import re
import csv
from lxml.html import fromstring
from crawler.crawler import link_crawler

def scrape_callback(url, html):
    """
    A typical scraper for extracting data: uses tutorial site as an
    example
    """
    fields = ('area', 'population', 'iso', 'country', 'capital', 'continent',
              'tld', 'currency_code', 'currency_name', 'phone',
              'postal_code_format', 'postal_code_regex', 'languages',
              'neighbours')
    if re.search(r'/view/', url):
        tree = fromstring(html)
        all_rows = [
                tree.xpath('//tr[@id="places_%s__row"]/td[@class="w2p_fw"]' %
                    field)[0].text_content() for field in fields]
        print(url, all_rows)

class CsvCallback:
    """
    extracts and stores data as a csv file
    """

    def __init__(self):
        self.writer = csv.writer(open('data/countries.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital', 'continent',
                       'tld', 'currency_code', 'currency_name', 'phone',
                       'postal_code_format', 'postal_code_regex', 'languages',
                       'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search(r'/view/', url):
            tree = fromstring(html)
            all_rows = [
                    tree.xpath('//tr[@id="places_%s__row"]/td[@class="w2p_fw"]' %
                        field)[0].text_content() for field in self.fields]
            self.writer.writerow(all_rows)
