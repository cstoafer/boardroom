import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
FORM_INDEX_DIR = os.path.join(DATA_DIR, 'form_index')
FORM_CACHE_DIR = os.path.join(DATA_DIR, 'form_cache')

EDGAR_BASEURL = 'https://www.sec.gov/Archives/'

email = ''

