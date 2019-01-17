"""

Implements objects for caching content
"""

import os
import re
from urllib.parse import urlsplit
import json
import zlib
from datetime import datetime, timedelta
from redis import StrictRedis

class DiskCache:

    def __init__(self, cache_dir='cache', max_len=255, compress=True,
            encoding='utf-8', expires=timedelta(days=30)):
        self.cache_dir = cache_dir
        self.max_len = max_len
        self.compress = compress
        self.encoding = encoding
        self.expires = expires

    def url_to_path(self, url):
        """
        Return file system path string for given URL
        """
        components = urlsplit(url)
        path = components.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        filename = components.netloc + path + components.query
        # replace invalid characters
        filename = re.sub(r'[^/0-9a-zA-Z\-.,;_]', '_', filename)
        # restrict max num of characters
        filename = '/'.join(seg[:self.max_len] for seg in filename.split('/'))
        return os.path.join(self.cache_dir, filename)

    def __getitem__(self, url):
        """
        Load data from disk for given url
        """
        path = self.url_to_path(url)
        if path.endswith('index'):
            path += '/'
            path = self.url_to_path(path)
        if os.path.exists(path):
            mode = ('rb' if self.compress else 'r')
            with open(path, mode) as fp:
                if self.compress:
                    data = zlib.decompress(fp.read()).decode(self.encoding)
                    data = json.loads(data)
                else:
                    data = json.load(fp)
            exp_date = data.get('expires')
            if exp_date and (datetime.strptime(exp_date, '%Y-%m-%dT%H:%M:%S')
                             <= datetime.utcnow()):
                print('cache expired!', exp_date)
                raise KeyError(url + 'has expired.')
            return data
        else:
            # URL not yet cached
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """
        Save data to disk for given url
        """
        path = self.url_to_path(url)
        if path.endswith('index'):
            path += '/'
            path = self.url_to_path(path)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        mode = ('wb' if self.compress else 'w')
        result['expires'] = (datetime.utcnow() +
                             self.expires).isoformat(timespec='seconds')
        with open(path, mode) as fp:
            if self.compress:
                data = bytes(json.dumps(result), self.encoding)
                fp.write(zlib.compress(data))
            else:
                json.dump(result, fp)

class RedisCache:

    def __init__(self, client=None, expires=timedelta(days=30),
                 encoding='utf-8', compress=True):
        # if client not passed, connect to redis using localhost port
        self.client = client
        if client is None:
            self.client = StrictRedis(host='localhost', port=6379, db=0)
        self.expires = expires
        self.encoding = encoding
        self.compress = compress

    def __getitem__(self, url):
        """
        Load value from redis with given url as key
        """
        record = self.client.get(url)
        if record:
            if self.compress:
                record = zlib.decompress(record)
            return json.loads(record.decode(self.encoding))
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """
        Save value in redis with given url as key
        """
        data = bytes(json.dumps(result), self.encoding)
        if self.compress:
            data = zlib.compress(data)
        self.client.setex(url, self.expires, data)

