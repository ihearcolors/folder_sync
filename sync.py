import os
import sys
import time
import logging
import argparse
from watchdog.observers.polling import PollingObserverVFS
from watchdog.events import FileSystemEventHandler

#  Parsing command-line arguments using argparse
parser = argparse.ArgumentParser(description="A script for synchronizing 2 folders",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--source", type=str, help="Source Folder", required=True)
parser.add_argument("-d", "--destination", type=str, help="Destination Folder", required=True)
parser.add_argument("-i", "--interval", type=float, help="Interval between sync in seconds", required=True)
parser.add_argument("-l", "--logfile", type=str, help="Log File", required=False)
args = vars(parser.parse_args())

#  Storing values from parsed arguments:
source = args['source']
dest = args['destination']
ival = args['interval']
log = args['logfile']
timestamp = time.ctime()  # Time and Date for printed logs

#  Configuring logging module
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename=log, filemode='a', level=logging.INFO)


#  Defining functions for event handling and actions to take
def on_created(event):
    print(f"{timestamp} [CREATE] \"{event.src_path}\"")
    logging.info(f'[SOURCE]  [CREATED]  \"{event.src_path}\"')
    # dst = '\\'.join(str(event.src_path).replace(path, dest).split('\\')[:-1])
    dst = str(event.src_path.replace(source, dest))
    try:
        if 'win' in sys.platform:
            if os.path.isfile(event.src_path):
                os.system(f"copy \"{event.src_path}\" \"{dst}\"")
                logging.info(f'[REPLICA] [CREATED]  \"{dst}\"')
            elif os.path.isdir(event.src_path):
                os.system(f"mkdir \"{str(event.src_path).replace(source, dest)}\"")
                logging.info(f'[REPLICA] [CREATED]  \"{dst}\"')
        else:
            if os.path.isfile(event.src_path):
                os.system(f"cp \"{event.src_path}\" \"{dst}\"")
                logging.info(f'[REPLICA] [CREATED]  \"{dst}\"')
            elif os.path.isdir(event.src_path):
                os.system(f"mkdir -p \"{str(event.src_path).replace(source, dest)}\"")
                logging.info(f'[REPLICA] [CREATED]  \"{dst}\"')
    except Exception as e:
        print("Error ", e)
        logging.error(f'[ERROR] {e}')


def on_deleted(event):
    print(f"{timestamp} [DELETE] \"{event.src_path}\"")
    logging.info(f'[SOURCE]  [DELETED] \"{event.src_path}\"')
    dst = str(event.src_path.replace(source, dest))
    try:
        if 'win' in sys.platform:
            if os.path.isdir(dst):
                os.system(f"rmdir /s /q \"{dst}\"")
                logging.info(f'[REPLICA] [DELETED] \"{dst}\"')
            elif os.path.isfile(dst):
                os.system(f"del /s /q \"{dst}\"")
                logging.info(f'[REPLICA] [DELETED] \"{dst}\"')
        else:
            if os.path.isdir(dst):
                os.system(f"rm -R {dst}")
                logging.info(f'[REPLICA] [DELETED] \"{dst}\"')
            elif os.path.isfile(dst):
                os.system(f"rm {dst}")
                logging.info(f'[REPLICA] [DELETED] \"{dst}\"')

    except Exception as e:
        print("Error ", e)
        logging.error(f'[ERROR] {e}')


def on_modified(event):
    print(f"{timestamp} [MODIFY] \"{event.src_path}\"")
    logging.info(f'[SOURCE]  [MODIFIED] \"{event.src_path}\"')
    dst = str(event.src_path.replace(source, dest))
    try:
        if 'win' in sys.platform:
            if os.path.isfile(event.src_path):
                os.system(f"copy \"{event.src_path}\" \"{dst}\"")
                logging.info(f'[REPLICA] [MODIFIED] \"{dst}\"')
            elif os.path.isdir(event.src_path):
                os.system(f"mkdir \"{str(event.src_path).replace(source, dest)}\"")
                logging.info(f'[REPLICA] [MODIFIED] \"{dst}\"')
        else:
            if os.path.isfile(event.src_path):
                os.system(f"cp \"{event.src_path}\" \"{dst}\"")
                logging.info(f'[REPLICA] [MODIFIED] \"{dst}\"')
            elif os.path.isdir(event.src_path):
                os.system(f"mkdir -p \"{str(event.src_path).replace(source, dest)}\"")
                logging.info(f'[REPLICA] [MODIFIED] \"{dst}\"')
    except Exception as e:
        print("Error ", e)
        logging.error(f'[ERROR] {e}')


def on_moved(event):
    print(f"[{timestamp}] [MOVE] \"{event.src_path} -> {event.dest_path}\"")
    logging.info(f'[SOURCE]  [MOVED]    \"{event.src_path} -> {event.dest_path}\"')
    dst = str(event.src_path.replace(source, dest))
    new_dst = str(event.dest_path.replace(source, dest))
    try:
        if 'win' in sys.platform:
            if os.path.isdir(dst):
                os.system(f"move \"{dst}\" \"{new_dst}\"")
                logging.info(f'[REPLICA] [MOVED]    \"{dst}\" -> \"{new_dst}\"')
            elif os.path.isfile(dst):
                os.system(f"move \"{dst}\" \"{new_dst}\"")
                logging.info(f'[REPLICA] [MOVED]    \"{dst}\" -> \"{new_dst}\"')
        else:
            os.system(f"mv \"{dst}\" \"{new_dst}\"")
            logging.info(f'[REPLICA] [MOVED]    \"{dst}\" -> \"{new_dst}\"')
    except Exception as e:
        print("Error ", e)
        logging.error(f'[ERROR] {e}')


#  Defining handler and initializing classes
handler = FileSystemEventHandler()
handler.on_created = on_created
handler.on_deleted = on_deleted
handler.on_modified = on_modified
handler.on_moved = on_moved

obs = PollingObserverVFS(os.stat, os.scandir, polling_interval=ival)
obs.schedule(handler, source, recursive=True)
obs.start()

#  Starting the main loop to continuously check for events:
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    obs.stop()
obs.join()
