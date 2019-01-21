"""
Main crawler
"""
import re
import threading
import time
from urllib.parse import urljoin, urlparse
import socket
from .utils.throttle import Throttle
from .utils.helpers import get_robots_parser
from .utils.downloader import Downloader
from .utils.helpers import get_links

SLEEP_TIME = 1
socket.setdefaulttimeout(120)

def threaded_crawler(start_url,link_regex, user_agent='wswp', proxies=None,
        delay=3, max_depth=4, num_retries=2, cache=None, max_threads=10,
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
    url_downloader = Downloader(delay=delay, user_agent=user_agent, proxies=proxies,
                                cache=cache)
    def process_queue():
        while crawl_queue:
            url = crawl_queue.pop()
            no_robots = False
            if not url or 'http' not in url:
                continue
            domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)
            robot_parser = robots.get(domain)
            if not robot_parser and domain not in robots:
                robots_url = '{}/robots.txt'.format(domain)
                # get the robot parser object
                robot_parser = get_robots_parser(robots_url)
                if not robot_parser:
                    # problem finding the robots.txt file, still crawl
                    no_robots = True
                robots[domain] = robot_parser
            elif domain in robots:
                no_robots = True
            # check url passes robots.txt restrictions
            if no_robots or robot_parser.can_fetch(user_agent, url):
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

    threads = []
    print(max_threads)
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        print(threads)
        for thread in threads:
            thread.join()
        time.sleep(SLEEP_TIME)

