import os
import errno
import cPickle as pickle

import config

def save_cache_dict(datadict, filename, directory=config.DATA_DIR):
    filepath = os.path.join(directory, filename)
    with open(filepath, 'wb') as f:
        pickle.dump(datadict, f)

def load_cache_dict(filename, directory=config.DATA_DIR):
    filepath = os.path.join(directory, filename)
    if not os.path.isfile(filepath):
        return dict()
    with open(filepath, 'rb') as f:
        datadict = pickle.load(f)
    return datadict

def silentremove(filepath):
    """Removes a file and ignores error if file does not exist."""
    try:
        os.remove(filepath)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured
