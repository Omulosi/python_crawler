import re
import csv
from zipfile import ZipFile
from io import TextIOWrapper, BytesIO
import requests
from lxml.html import fromstring
from crawler.crawler import link_crawler
from crawler.threaded_crawler import threaded_crawler

def scraper_callback(url, html):
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


class AlexaCallback:

    def __init__(self, max_urls=500):
        self.max_urls = max_urls
        self.seed_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
        self.urls = []

    def __call__(self):
        resp = requests.get(self.seed_url, stream=True)
        with ZipFile(BytesIO(resp.content)) as zf:
            csv_filename = zf.namelist()[0]
            with zf.open(csv_filename) as csv_file:
                for _, website in csv.reader(TextIOWrapper(csv_file)):
                    self.urls.append('http://' + website)
                    if len(self.urls) == self.max_urls:
                        break

if __name__ == '__main__':
    from crawler.utils.cache import RedisCache
    from time import time
    import argparse

    parser = argparse.ArgumentParser(description='Threaded Link Crawler')
    parser.add_argument('max_threads', type=int, help='maximum number of threads', 
            nargs='?', default=5)
    parser.add_argument('url_pattern', type=str, help='regex pattern for url\
            matching', nargs='?', default='$^')
    par_args = parser.parse_args()

    AC = AlexaCallback()
    AC()
    start_time = time()
    link_crawler(AC.urls, '$^', cache=RedisCache())
    # print('Total time: %ss' % (time() - start_time))

    # threaded_crawler(AC.urls, par_args.url_pattern, cache=RedisCache(),
    #        max_threads=par_args.max_threads)
    print('Total time: %ss' % (time() - start_time))
