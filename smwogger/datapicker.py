import requests


class DataPicker(object):
    def __init__(self, data_url=None):
        if data_url is None:
            self.data = {}
        else:
            self.data = requests.get(data_url).json()
