"""
Main crawler
"""
import re
from urllib.parse import urljoin, urlparse
import socket
from .utils.throttle import Throttle
from .utils.helpers import get_robots_parser
from .utils.downloader import Downloader
from .utils.helpers import get_links

socket.setdefaulttimeout(60)

def link_crawler(start_url, link_regex, robots_url=None, user_agent='wswp',
        max_depth=-1, delay=2, proxies=None, num_retries=2, cache=None,
        scraper_callback=None):
    """
    Crawl from the given start url and follow links matched
    by link_regex

    max_depth initially set to -1 to not set a limit on crawl depth
    """
    if isinstance(start_url, list):
        crawl_queue = start_url
    else:
        crawl_queue = [start_url]
    # keep track of seen urls
    seen, robots = {}, {}

    #if robots_url is None:
    #    robots_url = '{}/robots.txt'.format(start_url)
    #rp = get_robots_parser(robots_url)
    url_downloader = Downloader(delay=delay, user_agent=user_agent, proxies=proxies,
            cache=cache)
    #seen = {start_url: 0}
    #data = []
    while crawl_queue:
        url = crawl_queue.pop()
        no_robots = False
        if 'http' not in url:
            continue
        domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)
        rp = robots.get(domain)
        if not rp and domain not in robots:
            robots_url = '{}/robots.txt'.format(domain)
            rp = get_robots_parser(robots_url)
            if not rp:
                no_robots = True
            robots[domain] = rp
        elif domain in robots:
            no_robots = True
        # check url passe robots.txt restrictions
        if no_robots or rp.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                print('Skipping %s due to depth' % url)
                continue
            html = url_downloader(url, num_retries=num_retries)
            if not html:
                continue
            if scraper_callback:
                links = scraper_callback(url, html) or []
            else:
                links = []
            # filter for links matching regular expression
            for link in get_links(html) + links:
                if re.search(link_regex, link) and not re.search(r'next',
                        link):
                    if 'http' not in link:
                        if link.startswith('//'):
                            link = '{}:{}'.format(urlparse(url).scheme, link)
                        elif link.startswith('://'):
                            link = '{}{}'.format(urlparse(url).scheme, link)
                        else:
                            link = urljoin(domain, link)
                    #abs_link = urljoin(start_url, link)
                    if link not in seen:
                        seen[link] = depth + 1
                        crawl_queue.append(link)
        else:
            print('Blocked by robots.txt:', url)


