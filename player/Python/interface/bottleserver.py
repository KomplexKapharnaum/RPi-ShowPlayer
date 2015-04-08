
import sys
import os


# SET PYTHON PATH IN PARENT DIR
def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(os.path.abspath(fname))
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)
    # print(PythonPath)

set_python_path(depth=1)


from libs.bottle import Bottle, run, static_file, response, request
from engine.setting import settings
import json

app = Bottle()
staticpath = os.path.dirname(os.path.realpath(__file__))+'/www/'
scenariopath = settings.get("path", "scenario")

# TEST Json save
@app.route('/test')
def test():
    return '<form action="/save/test.json" method="post">Json <input type="text" name="content" /><input type="submit" value="Save" /></form>'


# LOAD Json
@app.route('/load/<filepath:path>')
def load(filepath):
    response.content_type = 'application/json'
    filepath = scenariopath+"/"+filepath
    try:
        with open(filepath, 'r') as file:   # Use file to refer to the file object
            return file.read()
    except:
        answer = dict()
        answer['status'] = 'error'
        answer['message'] = 'File not found'
        return json.dumps(answer)


# SAVE Json
@app.route('/save/<filepath:path>')
def save(filepath):
    response.content_type = 'application/json'
    answer = dict()
    answer['status'] = 'error'
    answer['message'] = 'No content received'
    return json.dumps(answer)


# SAVE Json
@app.route('/save/<filepath:path>', method='POST')
def save(filepath):
    response.content_type = 'application/json'
    content = request.forms.get('content')
    answer = dict()
    json.loads(content)
    try:
        json.loads(content)
        #test if valid json
    except:
        answer['status'] = 'error'
        answer['message'] = 'JSON not valid'
        return json.dumps(answer)

    try:
        path = scenariopath
        if not os.path.exists(path):
            os.makedirs(path)
        path = path+"/"+filepath
        print path
        with open(path, 'w') as file:
            file.write(content)
    except:
        answer['status'] = 'error'
        answer['message'] = 'Write Error'
        return json.dumps(answer)

    answer['status'] = 'success'
    return json.dumps(answer)

# Static index
@app.route('/')
def server_index():
    return static_file('index.html', root=staticpath)

# Static content
@app.route('/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=staticpath)

@app.route('/hello')
def hello():
    return "Hello World!"


run(app, host='0.0.0.0', port=8080)
