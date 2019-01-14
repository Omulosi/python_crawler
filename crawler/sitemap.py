"""
crawls a sitemap
"""
import re
from .utils.helpers import download

def crawl_sitemap(url):
    # Download sitemap file
    sitemap = download(url)
    # extract sitemap links
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    # download each link
    for link in links:
        html = download(link)
        # scrape html here

