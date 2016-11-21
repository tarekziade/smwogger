import requests
import json
import os


class DataPicker(object):
    def __init__(self, data=None):
        if data is None:
            self.data = {}
        else:
            self.data = data
        self._vars = {}

    def scenario(self):
        return self.data.get('scenario', [])

    def path(self, path, **extra):
        vars = dict(self.data.get('path', {}))
        vars.update(self._vars)
        vars.update(extra)
        return path.format(**vars)

    def set_var(self, name, value):
        self._vars[name] = value

    def get_var(self, name):
        return self._vars[name]
