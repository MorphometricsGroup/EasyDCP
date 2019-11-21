import os
import shutil
import time

def make_dir(dir_path, clean=False):
    if os.path.exists(dir_path):
        if clean:
            shutil.rmtree(dir_path)
            time.sleep(1)  # ensure the folder is cleared
            os.mkdir(dir_path)
    else:
        os.mkdir(dir_path)
