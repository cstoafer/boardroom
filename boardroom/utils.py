import os
import errno
try:
    import cPickle as pickle
except ImportError:
    import pickle
import gzip
import csv

from boardroom import config


def read_file(inpath):
    if os.path.exists(inpath + '.gz'):
        inpath += '.gz'
    if inpath.endswith('.gz'):
        with gzip.open(inpath, 'rt', encoding='utf8') as f:
            content = f.read()
    else:
        with open(inpath) as f:
            content = f.read()
    return content


def save_file(outpath, text, compress=True):
    if compress is True:
        text = gzip.compress(text)
        if not outpath.endswith('.gz'):
            outpath += '.gz'
    with open(outpath, 'wb') as o:
        o.write(text)


def makedirs(dirpath):
    """
    Checks if `dirpath` exists and makes it if it doesn't.
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


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


def get_form_index_fpath(year):
    fname = '{}.psv'.format(year)
    return os.path.join(config.FORM_INDEX_DIR, fname)


def form_loc_iter(year, delimiter='|', cik=None):
    fpath = get_form_index_fpath(year)
    with open(fpath, 'r') as f:
        csvreader = csv.reader(f, delimiter=delimiter)
        for row in csvreader:
            if cik is None or row[2] == cik:
                yield row
