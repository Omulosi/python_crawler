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
        robot_parser = robotparser.RobotFileParser()
        robot_parser.set_url(robots_url)
        robot_parser.read()
        return robot_parser
    except Exception as e:
        print('Error finding robots url:', robots_url, e)

def get_links(html):
    """
    Return a list of links from an html page
    """
    webpage_regex = re.compile("""<a[ ]+href=["'](.*?)["']""",
            re.IGNORECASE)
    return webpage_regex.findall(html)

