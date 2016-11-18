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
        self._vars = {}

    def scenario(self):
        return self.data.get('scenario', [])

    def path(self, path):
        vars = dict(self.data.get('path', {}))
        vars.update(self._vars)
        return path.format(**vars)

    def set_var(self, name, value):
        self._vars[name] = value

    def get_var(self, name):
        return self._vars[name]
