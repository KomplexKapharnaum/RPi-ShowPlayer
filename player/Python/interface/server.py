
import sys
import os
import time
from os import listdir
from os.path import isfile, join, isdir
from modules import DECLARED_OSCROUTES, DECLARED_PUBLICSIGNALS, DECLARED_PUBLICBOXES
from engine.log import init_log
from engine.media import save_scenario_on_fs
from engine.threads import patcher
from engine import fsm, tools
from libs import oscack
import modules
import scenario.pool
from engine.setting import settings, devicesV2
from libs.bottle import Bottle, run, static_file, response, request, redirect
import json

log = init_log("webserver")

# SET PYTHON PATH IN PARENT DIR
def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(os.path.abspath(fname))
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)
    # print(PythonPath)

set_python_path(depth=1)


app = Bottle()
staticpath = os.path.dirname(os.path.realpath(__file__))+'/www/'
scenariopath = settings.get_path("scenario", "activescenario")
if not os.path.exists(scenariopath):
    try:
        os.makedirs(scenariopath)
    except OSError as e:
        log.exception(log.show_exception(e))
mediapath = settings.get_path("media")


def sendjson(data):
    response.content_type = 'application/json'
    if 'callback' in request.query:
        return request.query['callback'] + "(" + json.dumps(data) + ")"
    return json.dumps(data)

@app.route('/info')
def info():
    answer = dict()
    answer['timeline'] = dict()
    answer['timeline']['group'] = scenario.pool.timeline_group
    answer['timeline']['version'] = scenario.pool.timeline_version

    answer['timeline']['activescene'] = scenario.CURRENT_FRAME
    answer['timeline']['scenes'] = [scene.uid for scene in scenario.pool._Timeline]
    try:
        answer['timeline']['signals'] = scenario.pool.Frames[scenario.CURRENT_FRAME]._get_all_reachabled_signals(settings.get("uName"))
    except (IndexError, KeyError):
        answer['timeline']['signals'] = list()


    answer['device'] = dict()
    answer['device']['name'] = settings.get("uName")
    answer['device']['voltage'] = modules.devicecontrol.TENSION
    try:
        answer['device']['settings'] = devicesV2.get(settings.get("uName"))
    except KeyError:
        answer['device']['settings'] = {}
    answer['device']['state'] = scenario.pool.State

    answer['system'] = dict()
    answer['system']['branch'] = tools.get_git_branch()
    answer['system']['commit'] = list(tools.get_git_last_commit())

    return sendjson(answer)

@app.route('/changeScene', method='POST')
def changeScene():
    scene = request.forms.get('scene')
    modules.scenecontrol.scene_force_to(int(scene))
    return 'ok'

@app.route('/sendSignal', method='POST')
def sendSignal():
    signalName = request.forms.get('signal')
    signal = fsm.Flag(signalName).get()
    patcher.patch(signal)
    log.info("Webinterface send signal : {}".format(signalName))
    return 'ok'

@app.route('/medialist')
def medialist():
    answer = dict()
    answer['all'] = []
    answer['audio'] = []
    answer['video'] = []
    answer['txt'] = []

    path = settings.get_path('media', 'video')
    if isdir(path):
        for f in listdir(path):
            if f[0] != '.':
                answer['video'].append(f)

    path = settings.get_path('media', 'audio')
    if isdir(path):
        for f in listdir(path):
            if f[0] != '.':
                answer['audio'].append(f)

    path = settings.get_path('media', 'text')
    if isdir(path):
        for f in listdir(path):
            if f[0] != '.':
                answer['txt'].append(f)

    for i, liste in answer.items():
        answer[i] = sorted(liste)

    return sendjson(answer)


@app.route('/disposList')
def dispoList():
    response.content_type = 'application/json'
    path = settings.get_path('deviceslistV2')
    try:
        answer = dict()
        with open(path, 'r') as file:   # Use file to refer to the file object
            answer = json.loads( file.read() )
        answer['status'] = 'success'
        return sendjson(answer)
    except:
        answer = dict()
        answer['status'] = 'error'
        answer['message'] = 'File not found'
        return sendjson(answer)


@app.route('/library')
def librarylist():
    answer = dict()
    answer['functions'] = []
    answer['signals'] = []
    # SENDSIGNAL BOXES FOR DECLARED OSC ROUTES
    for oscpath, route in DECLARED_OSCROUTES.items():
        box = {
            'name': oscpath.split('/')[-1].upper(),
            'category': oscpath.split('/')[1].upper(),
            'dispos': ('dispo' in route['args']),
            'medias': ('media' in route['args']),
            'arguments': [arg for arg in route['args'] if arg != 'dispo' and arg != 'media'],
            'code': '#HARDCODED scenario.functions.add_signal()',
            'hard': True
        }
        answer['functions'].append(box)
    # PUBLIC BOXES
    for name, box in DECLARED_PUBLICBOXES.items():
        box = {
            'name': name.replace('_PUBLICBOX', ''),
            'category': box['category'].upper(),
            'dispos': ('dispo' in box['args']),
            'medias': ('media' in box['args']),
            'arguments': [arg for arg in box['args'] if arg != 'dispo' and arg != 'media'],
            'code': '#HARDCODED modules.publicboxes.'+box['function'].__name__,
            'hard': True
        }
        answer['functions'].append(box)
    # CABLES FOR DECLARED MODULE RCV SIGNALS
    for signal in DECLARED_PUBLICSIGNALS:
        answer['signals'].append(signal)
    answer['signals'] = sorted(answer['signals'])
    return sendjson(answer)


@app.route('/moduleslist')
def moduleslist():
    return sendjson([module for module in modules.MODULES.keys() if module not in settings.get('managers')])



# TEST Json save
# @app.route('/test')
# def test():
#     return '<form action="/save/test.json" method="post">Json <input type="text" name="content" /><input type="submit" value="Save" /></form>'

@app.route('/_SCENARIO/data/loadText.php', method='POST')
def loadText():
    response.content_type = 'application/json'
    filename = request.forms.get('filename')
    filetype = request.forms.get('type')
    try:
        path = mediapath+"/"+filename
        answer = dict()
        answer['status'] = 'success'
        with open(path, 'r') as file:   # Use file to refer to the file object
            answer['contents'] = file.read()
        return sendjson(answer)
    except:
        answer = dict()
        answer['status'] = 'error'
        answer['message'] = 'File not found'
        return sendjson(answer)


@app.route('/_SCENARIO/data/saveText.php', method='POST')
def saveText():
    response.content_type = 'application/json'
    filename = request.forms.get('filename')
    content = request.forms.get('contents')
    filetype = request.forms.get('type')
    timestamp = request.forms.get('timestamp')
    try:
        path = mediapath+"/"+filename
        answer = dict()
        with open(path, 'w') as file:
            file.write(content)
    except:
        answer['status'] = 'error'
        answer['message'] = 'Write Error'
        return sendjson(answer)

    answer['status'] = 'success'
    return sendjson(answer)


@app.route('/_TIMELINE/data/save.php', method='POST')
@app.route('/_SCENARIO/data/save.php', method='POST')
def save():
    response.content_type = 'application/json'
    filename = request.forms.get('filename')
    content = request.forms.get('contents')
    filetype = request.forms.get('type')
    timestamp = request.forms.get('timestamp')
    answer = dict()
    try:
        contjson = json.loads(content)
        #test if valid json
    except Exception as e:
        log.exception(log.show_exception(e))
        answer['status'] = 'error'
        answer['message'] = 'JSON not valid'
        return sendjson(answer)

    try:
        path = scenariopath
        path = path+"/"+filetype+'_'+filename+".json"
        with open(path, 'w') as file:
            file.write(json.dumps(contjson, indent=4, sort_keys=True))
    except:
        answer['status'] = 'error'
        answer['message'] = 'Write Error'
        return sendjson(answer)

    answer['status'] = 'success'
    save_scenario_on_fs(settings["current_timeline"], date_timestamp=float(timestamp)/1000.0)
    patcher.patch(fsm.Flag("DEVICE_RELOAD").get())
    oscack.protocol.scenariosync.machine.append_flag(oscack.protocol.scenariosync.flag_timeout.get())    # Force sync
    return sendjson(answer)

@app.route('/_TIMELINE/data/load.php', method='POST')
@app.route('/_SCENARIO/data/load.php', method='POST')
def load():
    response.content_type = 'application/json'
    filename = request.forms.get('filename')
    filetype = request.forms.get('type')
    path = scenariopath+"/"+filetype+'_'+filename+".json"
    try:
        answer = dict()
        answer['status'] = 'success'
        with open(path, 'r') as file:   # Use file to refer to the file object
            answer['contents'] = file.read()
        return sendjson(answer)
    except:
        answer = dict()
        answer['status'] = 'error'
        answer['message'] = 'File not found'
        return sendjson(answer)

@app.route('/_TIMELINE/data/fileDelete.php', method='POST')
@app.route('/_SCENARIO/data/fileDelete.php', method='POST')
def delete():
    filetype = request.forms.get('type')
    filename = request.forms.get('filename')
    path = scenariopath+"/"+filetype+'_'+filename+".json"
    answer = dict()
    try:
        os.remove(path)
        answer['status'] = 'success'
        answer['message'] = 'File deleted'
    except:
        answer['status'] = 'error'
        answer['message'] = 'File not found'
    return sendjson(answer)


@app.route('/_TIMELINE/data/fileRename.php', method='POST')
@app.route('/_SCENARIO/data/fileRename.php', method='POST')
def rename():
    filetype = request.forms.get('type')
    oldname = request.forms.get('oldname')
    oldname = scenariopath+"/"+filetype+'_'+oldname+".json"
    newname = request.forms.get('newname')
    newname = scenariopath+"/"+filetype+'_'+newname+".json"
    try:
        os.rename(oldname, newname)
        answer['status'] = 'success'
        answer['message'] = 'File deleted'
    except:
        answer['status'] = 'error'
        answer['message'] = 'File not found'
    return sendjson(answer)


@app.route('/_TIMELINE/data/fileList.php', method='POST')
@app.route('/_SCENARIO/data/fileList.php', method='POST')
def filelist():
    filetype = request.forms.get('type')
    path = scenariopath+"/"
    onlyfiles = list()
    #onlyfiles.append(filetype+"_"+filetype+".json")
    if os.path.exists(path):
        onlyfiles = [ f.replace(filetype+"_",'') for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.startswith(filetype+"_") ]
    return sendjson(onlyfiles)


# Static index
@app.route('/')
@app.route('/_CTRL')
def server_index():
    redirect("/_CTRL/index.html")

@app.route('/_TIMELINE')
def server_index():
    redirect("/_TIMELINE/index.html")

# Static content
@app.route('/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=staticpath)

@app.route('/hello')
def hello():
    return "Hello World!"


def start():
    while True:
        start_time = time.time()
        try:
            run(app, host='0.0.0.0', port=8080, quiet=True)
        except Exception as e:
            log.exception("Error in webserver : {}".format(e))
            if settings.get("webui", "autoreload", "enable") is not False:
                dt = time.time() - start_time
                if dt < float(settings.get("webui", "autoreload", "interval")):
                    time.sleep(float(settings.get("webui", "autoreload",
                                                  "interval"))-dt)
                continue
            else:
                break