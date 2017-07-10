import time

from boardroom import utils, ingestdata, parse_secform


def forms_from_ticker_iter(ticker, year_start, year_end, cache_files=False,
                            download_delay=0.5):
    """
    Retrieve trades of stock ticker in year range.
    """
    cik = ingestdata.ticker_to_cik(ticker)
    for year in range(int(year_start), int(year_end)+1):
        year = str(year)
        for row in utils.form_loc_iter(year, cik=cik):
            company_name = row[1]
            form_loc = row[4]
            form_dict, used_cache = parse_secform.get_form_dict(form_loc,
                                                        cache_file=cache_files)
            yield form_dict
            if used_cache is False:
                time.sleep(download_delay)


def get_trades_from_ticker(ticker, year_start, year_end):
    forms = forms_from_ticker_iter(ticker, year_start, year_end,
                                   cache_files=True)
    trades_all = []
    for form in forms:
        trades = form['nonderivative']['trades']
        for t in trades:
            t['issuer_cik'] = list(form['issuer'].keys())[0]
            t['insider_cik'] = list(form['owner'].keys())[0]
        trades_all.extend(trades)
    return trades_all


