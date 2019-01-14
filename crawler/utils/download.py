"""

utils.download
~~~~~~~~~~~~~~

Downloads a url

"""

import requests

def download(url, num_retries=2, user_agent='wswp', proxies=None):
    """
    Downloads the web page with the given url
    """
    print('Downloading:', url)
    headers = {'User-Agent': user_agent}
    try:
        resp = requests.get(url, headers=headers, proxies=proxies)
        html = resp.text
        if resp.status_code >= 400:
            print('Download error:', resp.text)
            html = None
            if num_retries and 500 <= resp.status_code < 600:
                # recursively retry 5xx HTTP errors
                return download(url, num_retries - 1)
    except requests.exceptions.RequestException as e:
        print('Download error:', e.reason)
        html = None

    return html

