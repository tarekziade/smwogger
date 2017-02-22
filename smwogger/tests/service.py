from bottle import response, Bottle, request
import os
import yaml


HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, 'absearch.yaml')
app = application = Bottle()


@app.route('/api.yaml')
def swagger_yaml():
    with open(SPEC) as f:
        data = f.read()
    response.set_header('Content-Type', 'text/yaml')
    return data


@app.route('/api.json')
def swagger():
    with open(SPEC) as f:
        data = yaml.load(f.read())
    return data


@app.route('/1/<path:path>')
def someapi(*args, **kw):
    return {}


@app.route('/badstatus')
def badstatus():
    return {'result': 'OK'}


@app.route('/')
def root():
    return {'result': 'OK'}


@app.route('/__heartbeat__')
def hb():
    return {'result': 'OK', 'headers': dict(request.headers)}
