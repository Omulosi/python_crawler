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
    try:
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception as e:
        print('Error finding robots url:', robots_url, e)

def get_links(html):
    """
    Return a list of links from an html page
    """
    webpage_regex = re.compile("""<a[ ]+href=["'](.*?)["']""",
            re.IGNORECASE)
    return webpage_regex.findall(html)

