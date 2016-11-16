import requests
import json
import os


class DataPicker(object):
    def __init__(self, data_url=None):
        if data_url is None:
            self.data = {}
        else:
            if os.path.exists(data_url):
                with open(data_url) as f:
                    self.data = json.loads(f.read())
            else:
                self.data = requests.get(data_url).json()

    def path(self, path):
        return path.format(**self.data.get('path', {}))
