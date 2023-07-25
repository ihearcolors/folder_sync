import os
import sys
import time
import logging
import argparse
from watchdog.observers.polling import PollingObserverVFS
from watchdog.events import FileSystemEventHandler

parser = argparse.ArgumentParser(description="A script for synchronizing 2 folders",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--source", type=str, help="Source Folder", required=True)
parser.add_argument("-d", "--destination", type=str, help="Destination Folder", required=True)
parser.add_argument("-i", "--interval", type=float, help="Interval between sync in seconds", required=True)
parser.add_argument("-l", "--logfile", type=str, help="Log File", required=False)
args = vars(parser.parse_args())

source = args['source']
dest = args['destination']
ival = args['interval']
log = args['logfile']
timestamp = time.ctime()  # Time and Date for Logs


def on_created(event):
    print(f"{timestamp} [CREATE] \"{event.src_path}\"")
    # dst = '\\'.join(str(event.src_path).replace(path, dest).split('\\')[:-1])
    dst = str(event.src_path.replace(source, dest))
    try:
        if 'win' in sys.platform:
            if os.path.isfile(event.src_path):
                # time.sleep(1)
                os.system(f"copy \"{event.src_path}\" \"{dst}\"")
                # print(fr"(win)copy {event.src_path} {dst}")
            elif os.path.isdir(event.src_path):
                os.system(f"mkdir \"{str(event.src_path).replace(source, dest)}\"")
                # print("created folder: ", str(event.src_path).replace(path, dest))
        else:
            if os.path.isfile(event.src_path):
                bs = "\\"
                os.system(f"cp \"{event.src_path}\" \"{dst}\"")
                # print(fr"copy {event.src_path} {dst}")
            elif os.path.isdir(event.src_path):
                os.system(f"mkdir -p \"{str(event.src_path).replace(source, dest)}\"")
                # print("created folder: ", str(event.src_path).replace(path, dest))
    except Exception as e:
        print("Error ", e)


def on_deleted(event):
    print(f"{timestamp} [DELETE] \"{event.src_path}\"")
    dst = str(event.src_path.replace(source, dest))
    try:
        if 'win' in sys.platform:
            if os.path.isdir(dst):
                os.system(f"rmdir /s /q \"{dst}\"")
                # print("deleted folder: ", str(event.src_path).replace(source, dst))
            elif os.path.isfile(dst):
                os.system(f"del /s /q \"{dst}\"")
                # print(f"Deleted {dst}")
        else:
            if os.path.isdir(dst):
                os.system(f"rm -R {dst}")
                print("deleted folder: ", {dst})
            elif os.path.isfile(dst):
                os.system(f"rm {dst}")
                print(f"Deleted {dst}")

    except Exception as e:
        print("Error ", e)


def on_modified(event):
    print(f"{timestamp} [MODIFY] \"{event.src_path}\"")


def on_moved(event):
    print(f"[{timestamp}] [MOVE] \"{event.src_path} -> {event.dest_path}\"")
    dst = str(event.src_path.replace(source, dest))
    new_dst = str(event.dest_path.replace(source, dest))
    # print(event.src_path, event.dest_path, dst, new_dst, sep='\r\n')
    try:
        if 'win' in sys.platform:
            if os.path.isdir(dst):
                os.system(f"move \"{dst}\" \"{new_dst}\"")
                # print(f"moved folder: \"{dst} -> {new_dst}\"")
            elif os.path.isfile(dst):
                os.system(f"move \"{dst}\" \"{new_dst}\"")
                # print(f"moved file: \"{dst} -> {new_dst}\"")
        else:
            os.system(f"mv \"{dst}\" \"{new_dst}\"")
    except Exception as e:
        print("Error ", e)


handler = FileSystemEventHandler()
handler.on_created = on_created
handler.on_deleted = on_deleted
# handler.on_modified = on_modified
handler.on_moved = on_moved

# my_observer = Observer()
obs = PollingObserverVFS(os.stat, os.scandir, polling_interval=ival)
obs.schedule(handler, source, recursive=True)
obs.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    obs.stop()
obs.join()