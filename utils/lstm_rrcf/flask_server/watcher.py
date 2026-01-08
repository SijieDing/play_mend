import signal
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys
import os
import resource
stop_event = False
class Watcher(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_script()

    def start_script(self):
        if self.process:
            process_temp = self.process
            self.process = None
            process_temp.terminate()
            process_temp.wait()  # Ensure the process is fully terminated
        
        print(f"Starting {self.script}...")
        env = os.environ.copy()
        self.process = subprocess.Popen([sys.executable, "-X", "frozen_modules=off", self.script], env=env)

    # def on_any_event(self, event):
    #     # if not stop_flag:  # Process events only if not shutting down
    #     print(f"Event detected: {event}")

    def on_modified(self, event):
        if event.src_path.find("/libs/") and event.src_path.find("/utests/")==-1 and event.src_path.endswith(".py"):
            print(f"Detected change in {event.src_path}, restarting...")
            self.start_script()

def handle_sigterm(signum, frame):
    print(f"Watch dog received SIGTERM ({signum}). Initiating graceful shutdown...")
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGINT)
    


if __name__ == "__main__":
    # Disable core dumps
    signal.signal(signal.SIGTERM, handle_sigterm)
    try:
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except (ValueError, resource.error) as e:
        print(f"Failed to disable core dumps: {e}")
    module_path = os.path.dirname(os.path.abspath(__file__))
    script_to_watch = module_path + "/server_v2/server.py"
    event_handler = Watcher(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
            event_handler.process.wait()
    observer.join()