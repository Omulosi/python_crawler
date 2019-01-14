"""
utils.helpers
~~~~~~~~~~~~~~

some utility functions that streamline the crawling process
"""
import re
from urllib import robotparser

def get_robots_parser(robots_url):
    """
    Return robot parser object using robots url
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp

def get_links(html):
    """
    Return a list of links rom html
    """
    webpage_regex = re.compile("""<a[ ]+href=["'](.*?)["']""",
            re.IGNORECASE)
    return webpage_regex.findall(html)

