"""
Defines a class that implements throttling
"""

from urllib.parse import urlparse
import time

class Throttle:
    """
    Add a delay between downloads to the same domain

    This class keeps track of when each domain was last accessed and
    will sleep if the time since last access was shorter than specified
    delay

    To implement throttling on a crwaler, call an instacen of this class
    before every download.

    >>> throttle = Throttle(delay)
    >>> throttle.wait(url)
    >>> html = download(url)

    """
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            # get seconds to wait before downloading from domain again
            sleep_secs = self.delay - (time.time() - last_accessed)
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        # update time domain was last accessed
        self.domains[domain] = time.time()
