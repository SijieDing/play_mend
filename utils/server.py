#!/usr/bin/env python
# Copyright (c) IBM Confidential
# PID 5698-OPE
# © Copyright IBM Corp. 2024, 2025
#
# This file use the code of https://github.ibm.com/z-aiops-unite/fission-environments/blob/develop/python/server.py

import importlib
import logging
import os
import signal
import sys
import json
import warnings
import re

from flask import Flask, request, abort
from gevent.pywsgi import WSGIServer
import bjoern
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask_sockets import Sockets
sys.path.extend(['/app/libs/nab_detection_pkg/nab_detection', '/app/libs/nab_detection_pkg/aiops_unite', '/app/libs/'])
import nab_detection
ENABLE_RDEBUG = os.environ.get('ENABLE_RDEBUG', False)
if ENABLE_RDEBUG == 'true':
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))  # Listen on all interfaces, port 5678
    print("Debugpy listening on port 5678...")  


IS_PY2 = (sys.version_info.major == 2)
SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
SENTRY_RELEASE = os.environ.get('SENTRY_RELEASE', None)
USERFUNCVOL = os.environ.get("USERFUNCVOL", "/userfunc")
RUNTIME_PORT = int(os.environ.get("RUNTIME_PORT", "8888"))

# configmaps and secrets will be placed into defined directories
DIR_CONFIGS = '/configs'
DIR_SECRETS = '/secrets'
RESOLVED_DIR_NAME = 'resolved_with_secrets'

DIR_RESOLVED_CONFIGS = os.path.join(DIR_CONFIGS, RESOLVED_DIR_NAME)

if SENTRY_DSN:
    params = {'dsn': SENTRY_DSN, 'integrations': [FlaskIntegration()]}
    if SENTRY_RELEASE:
        params['release'] = SENTRY_RELEASE
    sentry_sdk.init(**params)


def import_src(path):
    if IS_PY2:
        import imp
        return imp.load_source('mod', path)
    else:
        # the imp module is deprecated in Python3. use importlib instead.
        return importlib.machinery.SourceFileLoader('mod', path).load_module()


def store_specialize_info(state):
    json.dump(state, open(os.path.join(USERFUNCVOL, "state.json"), "w"))


def check_specialize_info_exists():
    return os.path.exists(os.path.join(USERFUNCVOL, "state.json"))


def read_specialize_info():
    return json.load(open(os.path.join(USERFUNCVOL, "state.json")))


def remove_specialize_info():
    os.remove(os.path.join(USERFUNCVOL, "state.json"))

def create_directory_if_not_exists(directory):
    print("directory: "+directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Created directory: "+ directory)

def list_immediate_dir_excluding_resolved(directory, exclude_resolved_dir=True):
    immediate_dirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    if exclude_resolved_dir:
        immediate_dirs =[ d for d in immediate_dirs if d!= RESOLVED_DIR_NAME]
    return immediate_dirs

def list_immediate_files(directory):
    immediate_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return immediate_files

def substitute_configmap_variables(inFile, outFile, logger):
    with open(inFile, 'r') as f:
        file_content = f.read()
    pattern =  r'"?\$\{([^\}]+)\}"?'
    def replace(match):
        variable_name = match.group(1)
        secret_file = os.path.join(DIR_SECRETS, variable_name)
        if os.path.exists(secret_file):
            with open(secret_file, 'r') as sf:
                secret_content = sf.read()
            processed_secret_content = '"'+secret_content.replace("\r", "\\r").replace("\n", "\\n")+'"'
            return processed_secret_content
        logger.info("secret file "+secret_file+" does not exist, skipping the env substitution for "+match.group(0))
        return match.group(0)
    resolved_content = re.sub(pattern, replace, file_content)
    with open(outFile, 'w') as f:
        f.write(resolved_content)
 
class SignalExit(SystemExit):

    def __init__(self, signo, exccode=1):
        super(SignalExit, self).__init__(exccode)
        self.signo = signo


def register_signal_handlers(signal_handler=signal.SIG_DFL):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

g_nab_detection = None
class FuncApp(Flask):

    def __init__(self, name, loglevel=logging.DEBUG):
        super(FuncApp, self).__init__(name)

        # init the class members
        self.userfunc = None
        self.root = logging.getLogger()
        self.ch = logging.StreamHandler(sys.stdout)

        #
        # Logging setup.  TODO: Loglevel hard-coded for now. We could allow
        # functions/routes to override this somehow; or we could create
        # separate dev vs. prod environments.
        #
        self.root.setLevel(loglevel)
        self.ch.setLevel(loglevel)
        self.ch.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.ch)

        if check_specialize_info_exists():
            self.logger.info('Found state.json')
            specialize_info = read_specialize_info()
            self.userfunc = self._load_v2(specialize_info)
            self.logger.info('Loaded user function {}'.format(specialize_info))

    def substituteAllConfigMaps(self):
        self.logger.info('/specialize called')
        self.logger.info('substitute configmaps started')
        create_directory_if_not_exists(DIR_RESOLVED_CONFIGS)
        config_namespace = list_immediate_dir_excluding_resolved(DIR_CONFIGS)
        for ns in config_namespace:
            self.logger.debug("namespace: "+ns)
            create_directory_if_not_exists(os.path.join(DIR_RESOLVED_CONFIGS, ns))
            configMaps = list_immediate_dir_excluding_resolved(os.path.join(DIR_CONFIGS, ns))
            for cm in configMaps:
                self.logger.debug("configmap: "+cm)
                create_directory_if_not_exists(os.path.join(DIR_RESOLVED_CONFIGS, ns, cm))
                config_files = list_immediate_files(os.path.join(DIR_CONFIGS, ns, cm))
                for f in config_files:
                    self.logger.debug("config file: "+f)
                    config_file = os.path.join(DIR_CONFIGS, ns, cm, f)
                    target_config_file = os.path.join(DIR_RESOLVED_CONFIGS, ns, cm, f)
                    substitute_configmap_variables(config_file, target_config_file, self.logger)
        for key, value in os.environ.items():
            if value.startswith("/configs/") and not value.startswith("/configs/"+ RESOLVED_DIR_NAME+ "/"):
                 nv = "/configs/"+ RESOLVED_DIR_NAME+ "/"+ value[len("/configs/"):]
                 self.logger.debug("- replacing environment variable "+ key +" with value of "+ nv)
                 os.environ[key] = nv 
        self.logger.debug("substitute configmaps done")

    def load(self):
        self.logger.info('/specialize called')
        # load user function from codepath
        self.userfunc = import_src('/userfunc/user').main
        return ""

    def loadv2(self):
        specialize_info = request.get_json()
        if check_specialize_info_exists():
            self.logger.warning("Found state.json, overwriting")
        self.userfunc = self._load_v2(specialize_info)
        store_specialize_info(specialize_info)
        return ""
    
    def substitute_config_and_load(self):
        self.substituteAllConfigMaps()
        return self.loadv2()

    def healthz(self):
        return "", 200

    def userfunc_call(self, *args):
        if self.userfunc is None:
            self.logger.error('userfunc is None')
            return abort(500)
        return self.userfunc(*args)

    def _load_v2(self, specialize_info):
        filepath = specialize_info['filepath']
        handler = specialize_info['functionName']
        self.logger.info(
            'specialize called with  filepath = "{}"   handler = "{}"'.format(
                filepath, handler))
        # handler looks like `path.to.module.function`
        parts = handler.rsplit(".", 1)
        if len(handler) == 0:
            # default to main.main if entrypoint wasn't provided
            moduleName = 'main'
            funcName = 'main'
        elif len(parts) == 1:
            moduleName = 'main'
            funcName = parts[0]
        else:
            moduleName = parts[0]
            funcName = parts[1]
        self.logger.debug('moduleName = "{}"    funcName = "{}"'.format(
            moduleName, funcName))

        # check whether the destination is a directory or a file
        if os.path.isdir(filepath):
            # add package directory path into module search path
            sys.path.append(filepath)

            self.logger.debug('__package__ = "{}"'.format(__package__))
            if __package__:
                mod = importlib.import_module(moduleName, __package__)
            else:
                mod = importlib.import_module(moduleName)

        else:
            # load source from destination python file
            mod = import_src(filepath)

        # load user function from module
        return getattr(mod, funcName)

    def signal_handler(self, signalnum, frame):
        self.logger.info('Received signal {}'.format(
            signal.strsignal(signalnum)))
        if check_specialize_info_exists():
            self.logger.info('Found state.json, removing')
            remove_specialize_info()
        signal.signal(signalnum, signal.SIG_DFL)
        raise SignalExit(signalnum)

    def nab_demo(self):
        global g_nab_detection
        if not g_nab_detection:
            g_nab_detection = nab_detection.start()
        return "Hello World! ", 200
    
def main():
    app = FuncApp(__name__, logging.DEBUG)
    sockets = Sockets(app)
    register_signal_handlers(app.signal_handler)

    app.add_url_rule('/specialize', 'load', app.load, methods=['POST'])
    app.add_url_rule('/v2/specialize', 'loadv2',app.substitute_config_and_load, methods=['POST'])
    app.add_url_rule('/healthz', 'healthz', app.healthz, methods=['GET'])
    app.add_url_rule(
        '/',
        'userfunc_call',
        app.userfunc_call,
        methods=['GET', 'POST', 'PUT', 'HEAD', 'OPTIONS', 'DELETE'])
    sockets.add_url_rule(
        '/',
        'userfunc_call',
        app.userfunc_call,
        methods=['GET', 'POST', 'PUT', 'HEAD', 'OPTIONS', 'DELETE'])
    app.add_url_rule('/nab_demo', 'nab_demo', app.nab_demo, methods=['GET'])
    #
    # TODO: this starts the built-in server, which isn't the most
    # efficient.  We should use something better.
    #
    if os.environ.get("WSGI_FRAMEWORK") == "GEVENT":
        app.logger.info("Starting gevent based server")
        from gevent_ws import WebSocketHandler
        svc = WSGIServer(('0.0.0.0', RUNTIME_PORT),
                         app,
                         handler_class=WebSocketHandler)
        svc.serve_forever()
    else:
        app.logger.info("Starting bjoern based server")
        bjoern.run(app, '0.0.0.0', RUNTIME_PORT, reuse_port=True)


main()
