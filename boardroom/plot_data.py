

def trade_to_line_shape(trade):
    buycolor = 'rgba(191, 128, 55, 0.3)'
    sellcolor = 'rgba(55, 191, 128, 0.3)'
    unkcolor = 'rgba(128, 128, 128, 0.3)'
    if trade['acquired_disposed_code'] == 'A':
        color = buycolor
    elif trade['acquired_disposed_code'] == 'D':
        color = sellcolor
    else:
        color = unkcolor
    line = {
        'type': 'line',
        'xref': 'x',
        'yref': 'paper',
        'x0': trade['date'],
        'y0': 0,
        'x1': trade['date'],
        'y1': 1,
        'line': {
            'color': color,
            'width': 1,
        },
    }
    return line


def build_graph(ticker, dates, prices, trades):
    graph = {'data': [{'x': dates, 'y': prices}],
             'layout': {
                 'title': '{}'.format(ticker.upper()),
                 'shapes': [trade_to_line_shape(trade) for trade in trades]
             }
             }
    return graph
