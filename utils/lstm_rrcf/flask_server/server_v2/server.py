#!/usr/bin/env python
# Copyright (c) IBM Confidential
# PID 5698-OPE
# © Copyright IBM Corp. 2024, 2025
#

import importlib
import logging
import os
import signal
import sys
import json
import re
import time
import threading

from flask import Flask, Response, request, abort, jsonify
from gevent.pywsgi import WSGIServer
import bjoern
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask_sockets import Sockets
from redis_client import init_redisclient, RedisClient
from logger import setup_logger, logger
import config

redisRequestCountKey = "fission-environment:request-counter"
redisResponseStatusHashKey = "fission-environment:response-counter"
redisLastUpdatedKey = "fission-environment:last-updated"

IS_PY2 = (sys.version_info.major == 2)
SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
SENTRY_RELEASE = os.environ.get('SENTRY_RELEASE', None)
USERFUNCVOL = os.environ.get("USERFUNCVOL", "/userfunc")
RUNTIME_PORT = int(os.environ.get("RUNTIME_PORT", "8888"))

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

class SignalExit(SystemExit):

    def __init__(self, signo, exccode=1):
        super(SignalExit, self).__init__(exccode)
        self.signo = signo


def register_signal_handlers(signal_handler=signal.SIG_DFL):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

class FuncApp(Flask):

    def __init__(self, name, loglevel=logging.DEBUG):
        super(FuncApp, self).__init__(name)

        # init the class members
        self.userfunc = None
        self.nab_detection_stopHandler = False
        self.shutdown_Handler = None

        if check_specialize_info_exists():
            logger.info('Found state.json')
            specialize_info = read_specialize_info()
            self.userfunc = self._load_v2(specialize_info)
            logger.info('Loaded user function {}'.format(specialize_info))

        @self.after_request
        def log_request_and_response(response):
            track_paths = ["/"]

            if request.path not in track_paths or not RedisClient.is_initialized():
                return response

            connected = False
            try:
                connected = RedisClient.connect()
                if not connected:
                    return response

                # Increment request counter
                RedisClient.incr(redisRequestCountKey)

                # Increment response counter
                response.direct_passthrough = False
                code_str = str(response.status_code)
                RedisClient.hincrby(redisResponseStatusHashKey, code_str)
                RedisClient.setTimestamp(redisLastUpdatedKey)

            except Exception as e:
                logger.error(f"Error updating metrics: {e}", exc_info=True)

            return response

        
    def load(self):
        logger.info('/specialize called')
        # load user function from codepath
        self.userfunc = import_src('/userfunc/user').main
        return ""

    def loadv2(self):
        specialize_info = request.get_json()
        if check_specialize_info_exists():
            logger.warning("Found state.json, overwriting")
        self.userfunc = self._load_v2(specialize_info)
        store_specialize_info(specialize_info)
        return ""
    
    def loadv3(self):
        self.userfunc, self.shutdown_Handler = self._load_v3()
        if self.userfunc is None:
            logger.error('Specialization failed. userfunc is None.')
        return ""

    def healthz(self):
        return "", 200

    def metrics(self):
        lines = []

        if RedisClient.is_initialized():
            try:
                connected = RedisClient.connect()
                if connected:
                    # HELP and TYPE for requests
                    lines.append("# HELP api_requests_total Total API requests")
                    lines.append("# TYPE api_requests_total counter")

                    # Get request count from Redis
                    req_count = int(RedisClient.get(redisRequestCountKey) or 0)
                    lines.append(f"api_requests_total {req_count}")

                    # HELP and TYPE for responses
                    lines.append("\n")
                    lines.append("# HELP api_responses_total Total API responses by status code")
                    lines.append("# TYPE api_responses_total counter")

                    # Get response counts from Redis
                    status_counts = RedisClient.hgetall(redisResponseStatusHashKey)
                    for status, count in status_counts.items():
                        lines.append(f'api_responses_total{{status="{status}"}} {int(count)}')

                    # HELP and TYPE for last updated timestamp
                    lines.append("\n")
                    lines.append("# HELP api_last_updated Last updated timestamp of API")
                    lines.append("# TYPE api_last_updated gauge")

                    # Get last updated timestamp
                    timestamp_info = RedisClient.getTimestamp(redisLastUpdatedKey)
                    if timestamp_info:
                        formatted_date = timestamp_info["formatted_date"]
                        timestamp_number = timestamp_info["timestamp_number"]
                        lines.append(f'api_last_updated{{date="{formatted_date}"}} {timestamp_number}')

            except Exception as e:
                logger.error(f"Error collecting metrics: {e}", exc_info=True)
                lines.append(f"# ERROR collecting metrics: {e}")

        return Response("\n".join(lines), mimetype="text/plain")

    def nab_demo(self):
        if not self.nab_detection_stopHandler:
            from aiops_nab_detection.nab_detection import start as start_nab_detection_test
            self.nab_detection_stopHandler = start_nab_detection_test()
        return "Hello World! ", 200
    
    def userfunc_call(self, *args):
        if self.userfunc is None:
            logger.error('userfunc is None')
            return abort(500)
        return self.userfunc(*args)

    def _load_v2(self, specialize_info):
        filepath = specialize_info['filepath']
        handler = specialize_info['functionName']
        logger.info(
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
        logger.debug('moduleName = "{}"    funcName = "{}"'.format(
            moduleName, funcName))

        # check whether the destination is a directory or a file
        if os.path.isdir(filepath):
            # add package directory path into module search path
            sys.path.append(filepath)

            logger.debug('__package__ = "{}"'.format(__package__))
            if __package__:
                mod = importlib.import_module(moduleName, __package__)
            else:
                mod = importlib.import_module(moduleName)

        else:
            # load source from destination python file
            mod = import_src(filepath)

        # load user function from module
        return getattr(mod, funcName)

    def _load_v3(self):
        filepath = os.getenv("FILE_PATH")
        handler = os.getenv("FUNCTION_NAME")
        logger.info(
            'specialize called with  filepath = "{}"   handler = "{}"'.format(
                filepath, handler))
        try:
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
            logger.debug('moduleName = "{}"    funcName = "{}"'.format(
                moduleName, funcName))

            # check whether the destination is a directory or a file
            if os.path.isdir(filepath):
                # add package directory path into module search path
                sys.path.append(filepath)

                logger.debug('__package__ = "{}"'.format(__package__))
                if __package__:
                    mod = importlib.import_module(moduleName, __package__)
                else:
                    mod = importlib.import_module(moduleName)

            else:
                # load source from destination python file
                mod = import_src(filepath)
            
            # load user function from module
            main_func =  getattr(mod, funcName)
            shutdown_func = None
            try:
                shutdown_func = getattr(mod, "shutdown")
            except:
                pass
            return main_func, shutdown_func
        except Exception as e:
            logger.error(f"_load_v3 Failed: {e}", exc_info=True)
            return None, None


    def signal_handler(self, signalnum, frame):
        global running
        logger.info('Received signal {}'.format(signal.strsignal(signalnum)))
        if check_specialize_info_exists():
            logger.info('Found state.json, removing')
            remove_specialize_info()

        # Gracefully close Redis connections if initialized
        if RedisClient.is_initialized():
            logger.info('Shutting down Redis connections')
            RedisClient.quit()

        # Close all socket
        sock, wsgi_app = bjoern._default_instance
        sock.close()
        self.logger.info('Close bjoern socket')
        if self.nab_detection_stopHandler:
            self.nab_detection_stopHandler()
        else:
            # It try to call stop in project
            if self.shutdown_Handler:
                self.shutdown_Handler()

        running = False
        signal.signal(signalnum, signal.SIG_DFL)
        raise SignalExit(signalnum)

running = True
def run_bjoern_server(app, host='127.0.0.1', port=8000):
    """Run the Bjoern server in a separate thread."""
    try:
        bjoern.run(app, host, port, reuse_port=True)
    except KeyboardInterrupt:
        # Handle Ctrl+C within the server thread
        print("Server interrupted, shutting down...")
    finally:
        print("Bjoern server stopped") 

def main():    
    global redisRequestCountKey, redisResponseStatusHashKey, redisLastUpdatedKey
    cfg = config.get_config()
    if cfg:
        log_level = cfg["logLevel"]
        setup_logger(level=log_level)

        if str(cfg.get("enableServicabilityMetrics", "true")).lower() == "true":
            init_redisclient(cfg)
            functionUniqueName = os.getenv("FUNCTION_UNIQUE_NAME")
            if functionUniqueName:
                redisRequestCountKey = functionUniqueName + ":request-counter"
                redisResponseStatusHashKey = functionUniqueName + ":response-counter"
                redisLastUpdatedKey = functionUniqueName + ":last-updated"
            else:
                logger.always("FUNCTION_UNIQUE_NAME is not set. Using default Redis keys.")
        else:
            logger.always("Servicability metrics are disabled. Redis client not initialized.")
    else:
        logger.always("Configuration is missing. Logging and Redis setup skipped.")

    
    app = FuncApp(__name__, logging.DEBUG)
    app.loadv3()
    sockets = Sockets(app)
    register_signal_handlers(app.signal_handler)

    app.add_url_rule('/specialize', 'load', app.load, methods=['POST'])
    app.add_url_rule('/v2/specialize', 'loadv2', app.loadv2, methods=['POST'])
    app.add_url_rule('/healthz', 'healthz', app.healthz, methods=['GET'])
    app.add_url_rule('/metrics', 'metrics', app.metrics, methods=['GET'])
    app.add_url_rule('/nab_demo', 'nab_demo', app.nab_demo, methods=['GET'])
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
        # Run Bjoern in a separate thread
        server_thread = threading.Thread(target=run_bjoern_server, args=(app, '0.0.0.0', RUNTIME_PORT))
        server_thread.daemon = True  # Daemonize thread to exit when main program exits
        server_thread.start()
        logger.info("Start the bjoern sucessfully!")
        # Keep the main thread alive to listen for signals
        try:
            while running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Main thread received interrupt, shutting down...")
            exit(0)

main()