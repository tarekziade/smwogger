from bottle import response, Bottle
import os


HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, 'absearch.yaml')
app = application = Bottle()


@app.route('/__api__')
def swagger():
    with open(SPEC) as f:
        data = f.read()
    response.set_header('Content-Type', 'application/yaml')
    return data


@app.route('/')
def root():
    return {'result': 'OK'}


@app.route('/__heartbeat__')
def hb():
    return {'result': 'OK'}
