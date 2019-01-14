"""
Main crawler
"""
import re
from urllib.parse import urljoin
from .utils.throttle import Throttle
from .utils.helpers import get_robots_parser
from .utils.download import download
from .utils.helpers import get_links


def link_crawler(start_url, link_regex, robots_url=None, user_agent='wswp',
        max_depth=4, delay=2, scrape_callback=None):
    """
    Crawl from the given start url and follow links matched
    by link_regex
    """
    if robots_url is None:
        robots_url = '{}/robots.txt'.format(start_url)
    rp = get_robots_parser(robots_url)
    throttle = Throttle(delay)

    crawl_queue = [start_url]
    seen = {}
    data = []
    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                print('Skipping %s due to depth' % url)
                continue
            throttle.wait(url)
            html = download(url, user_agent=user_agent)
            if html is None:
                continue
            if scrape_callback:
                data.extend(scrape_callback(url, html) or [])

            # filter for links matching regular expression
            for link in get_links(html):
                if re.search(link_regex, link):
                    abs_link = urljoin(start_url, link)
                    print('Abs link:', abs_link)
                    if abs_link not in seen:
                        seen[abs_link] = depth + 1
                        crawl_queue.append(abs_link)
        else:
            print('Blocked by robots.txt:', url)

