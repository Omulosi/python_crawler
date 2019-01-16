"""
Main crawler
"""
import re
from urllib.parse import urljoin
from .utils.throttle import Throttle
from .utils.helpers import get_robots_parser
from .utils.downloader import Downloader
from .utils.helpers import get_links


def link_crawler(start_url, link_regex, robots_url=None, user_agent='wswp',
        max_depth=-1, delay=2, proxies=None, num_retries=2, cache=None,
        scraper_callback=None):
    """
    Crawl from the given start url and follow links matched
    by link_regex

    max_depth initially set to -1 to not set a limit on crawl depth
    """
    if robots_url is None:
        robots_url = '{}/robots.txt'.format(start_url)
    rp = get_robots_parser(robots_url)
    url_downloader = Downloader(delay=delay, user_agent=user_agent, proxies=proxies,
            cache=cache)
    crawl_queue = [start_url]
    seen = {start_url: 0}
    data = []
    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                print('Skipping %s due to depth' % url)
                continue
            html = url_downloader(url, num_retries=num_retries)
            if not html:
                continue
            if scraper_callback:
                data.extend(scraper_callback(url, html) or [])
            # filter for links matching regular expression
            for link in get_links(html):
                if re.search(link_regex, link) and not re.search(r'next',
                        link):
                    abs_link = urljoin(start_url, link)
                    if abs_link not in seen:
                        seen[abs_link] = depth + 1
                        crawl_queue.append(abs_link)
        else:
            print('Blocked by robots.txt:', url)

