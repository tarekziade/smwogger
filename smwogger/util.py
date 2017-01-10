import os
import mimetypes
import json
import yaml
import requests
from swagger_parser import SwaggerParser


_JSON_TYPES = ('application/vnd.api+json', 'application/json')
_YAML_TYPES = ('application/x-yaml', 'text/yaml')

if '.yaml' not in mimetypes.types_map:
    mimetypes.types_map['.yaml'] = 'application/x-yaml'


def _decoder(mime):
    if mime in _YAML_TYPES:
        return yaml.load
    # we'll just try json
    return yaml.load


def get_content(url):
    if os.path.exists(url):
        mime = mimetypes.guess_type(url)[0]
        with open(url) as f:
            return _decoder(mime)(f.read())
    else:
        resp = requests.get(url)
        content_type = resp.header.get('Content-Type', 'application/json')
        return _decoder(content_type)(requests.get(url).content)
