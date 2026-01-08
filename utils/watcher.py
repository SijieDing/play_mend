import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys
import os
import resource

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

    def on_modified(self, event):
        if event.src_path.find("/libs/") and event.src_path.find("/utests/")==-1 and event.src_path.endswith(".py"):
            print(f"Detected change in {event.src_path}, restarting...")
            self.start_script()

if __name__ == "__main__":
    # Disable core dumps
    try:
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except (ValueError, resource.error) as e:
        print(f"Failed to disable core dumps: {e}")

    script_to_watch = "server.py"
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
    observer.join()