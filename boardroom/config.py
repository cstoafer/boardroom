import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
FORM_INDEX_DIR = os.path.join(DATA_DIR, 'form_index')
FORM_CACHE_DIR = os.path.join(DATA_DIR, 'form_cache')
STOCK_PRICE_DIR = os.path.join(DATA_DIR, 'stock_price')

EDGAR_BASEURL = 'https://www.sec.gov/Archives/'
YAHOO_STRUCTURL = ('https://finance.yahoo.com/quote/{ticker}/history?'
                   'period1={dt_start}&period2={dt_end}&'
                   'interval=1d&filter=history&frequency=1d'
                   )

