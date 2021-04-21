import multiprocessing
import os
# Get the full path from the given directory
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def CheckIfPathExists(directory):
    return os.path.exists(directory)

def create_fullpath_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def DebugCommand(*input):
    print("DEBUG:-" , input)
    # pass


CPU_COUNTS = int(multiprocessing.cpu_count()/3 + 1)