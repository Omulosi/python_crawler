"""

utils.download
~~~~~~~~~~~~~~

Downloads a url

"""

import random
import requests
from throttle import Throttle

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'

class Downloader:
    """
    This class uses cache to download pages
    """

    def __init__(self, delay=5, user_agent=None, proxies=None, cache=None,
            timeout=60):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent or USER_AGENT
        self.proxies = proxies
        self.cache = cache or {}
        self.num_retries = None
        self.timeout = timeout

    def __call__(self, url, num_retries=2):
        """
        Returns html from a cache or downloads it
        """
        self.num_retries = num_retries
        try:
            result = self.cache[url]
            print('Loaded from cache:', url)
        except KeyError:
            result = None
        if result and self.num_retries and 500 <= result['code'] < 600:
            # server error so ignore result from cache. Need to re-download
            result = None
        if result is None:
            # Result not loades from cache so download it
            self.throttle.wait(url)
            proxies = random.choice(self.proxies) if self.proxies else None
            headers = {'User-Agent': self.user_agent}
            result = self.download(url, headers, proxies)
            self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxies):
        """
        Downloads the web page with the given url

        This method can be used for simple downloads
        that do not require caching or throttling
        """
        print('Downloading:', url)
        try:
            resp = requests.get(url, headers=headers, proxies=proxies,
                                timeout=self.timeout)
            html = resp.text
            if resp.status_code >= 400:
                print('Download error:', resp.text)
                html = None
                if self.num_retries and 500 <= resp.status_code < 600:
                    # recursively retry 5xx HTTP errors
                    self.num_retries -= 1
                    return self.download(url, headers, proxies)
        except requests.exceptions.RequestException as e:
            print('Download error:', e)
            return {'html': None, 'code': 500}
        return {'html': html, 'code': resp.status_code}
