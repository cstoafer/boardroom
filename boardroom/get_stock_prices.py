from boardroom import ingestdata


def get_stock_price_timeseries(ticker):
    ticker = ticker.upper()
    stock_dicts = ingestdata.get_stock_price_dicts(ticker)
    dates_prices = [(d['date'],d['close']) for d in stock_dicts if 'close' in d]
    dates, prices = zip(*dates_prices)
    return dates, prices
