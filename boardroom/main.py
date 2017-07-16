import shutil
import os
import datetime
import json

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
                  abort, render_template, flash
from contextlib import closing

import plotly

from boardroom import get_trades, get_stock_prices, plot_data


app = Flask(__name__)

# configuration
DATABASE = os.path.join(app.root_path, 'db.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'development')
DEBUG = True if SECRET_KEY == 'development' else False

# create the application
app.config.from_object(__name__)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def show_homepage():
    if request.method == 'POST':
        ticker = request.form['ticker']
        year_start = request.form['year_start']
        year_end = request.form['year_end']
        trades = get_trades.get_trades_from_ticker(ticker, year_start, year_end)
        dates, prices = get_stock_prices.get_stock_price_timeseries(ticker)
        graph_ids = ['graph-1']
        graph = [plot_data.build_graph(ticker, dates, prices, trades)]
        graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('home.html', form=request.form, trades=trades,
                               graphJSON=graphJSON, graph_ids=graph_ids)
    return render_template('home.html', form=None)


if __name__ == '__main__':
    app.run()
