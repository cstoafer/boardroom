import os
from ftplib import FTP
try:
    from StringIO import StringIO
except:
    from io import StringIO, BytesIO
import gzip
import csv
import datetime
from lxml import etree
import requests

from boardroom import utils
from boardroom import config

try:
    basestring
except NameError:
    basestring = str


def ticker_to_cik(ticker, use_cache=True, remove_leading_zeros=True):
    """
    Returns a company's CIK with their ticker symbol as input.

    The CIK (Central Index Key) is used by the SEC for data lookup for company.

    Args:
        ticker (str): company stock ticker symbol

    Examples:
        >>> ticker_to_cik('KO')
        u'21344'

    Returns:
        Unicode: CIK (Central Index Key) for company.
    """
    if not isinstance(ticker, basestring):
        raise TypeError('ticker needs to be a string')
    if use_cache:
        ticker_cik_dict = utils.load_cache_dict('ticker_cik.p')
        if ticker in ticker_cik_dict:
            cik = ticker_cik_dict[ticker]
            if remove_leading_zeros is True:
                cik = str(int(cik))
            return cik
    query = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&' \
            'CIK={}&count=100&output=xml'.format(ticker)
    r = requests.get(query)
    xml = r.text
    tree = etree.fromstring(xml)
    cik = tree.xpath('//cik//text()')[0]
    # if use_cache is True, then add the data to the cached dictionary
    if use_cache:
        ticker_cik_dict[ticker] = cik
        utils.save_cache_dict(ticker_cik_dict, 'ticker_cik.p')
    if remove_leading_zeros is True:
        cik = str(int(cik))
    return cik


def write_forms_index(input_src, output_path, form_types=('3','4','5'), output_delimiter='|'):
    """
    Parses input from SEC form index files and writes to csv.

    Writes a delimited file to ``output_path``.  Each line is:
        <form type>|<company name>|<CIK>|<form submission date>|<location on ftp.sec.gov>
    Note: lines are appended to file at output_path.

    Args:
        input_src (file stream): The content of the SEC form as a file stream,
            iterable by line.
        output_path (str): Filepath for output.
        form_types (Iterable): Form types to ingest. For insider trading activity these are
            forms 3, 4, 5, as described on the `SEC forms site <https://www.sec.gov/forms>`_.
        output_delimiter (char): Single character delimiter (as required by python's csv package).
            Defaults to '|'.

    """
    with open(output_path, 'ab') as writecsv:
        csvwriter = csv.writer(writecsv, delimiter=output_delimiter)
        csvreader = csv.reader(input_src, delimiter=' ', skipinitialspace=True)
        for row in csvreader:
            if row[0] not in form_types:
                continue
            if '' in row:
                row.remove('')
            company_name = ' '.join(row[1:-3])
            line = [row[0], company_name]
            line.extend(row[-3:])
            csvwriter.writerow(line)


def get_forms_index(years=range(1993,datetime.datetime.now().year+1),
                    output_dir='data/form_index/', overwrite=False, form_types=('3','4','5'),
                    output_delimiter='|', email=config.email):
    """
    Opens the SEC index by form category, parses the content, and saves to csv files.

    The SEC indices are a list of forms that were submitted in a given time period. The index
    contains: form type, company name, date of submission, and location of document on ftp.sec.gov.

    In this function, the indices are collected for each year in ``years`` and output to the
    directory ``output_dir``, one csv file for each year. This only needs to be run once when
    building a local index.

    Writes a delimited file to ``output_path``.  Each line is:
        <form type>|<company name>|<CIK>|<form submission date>|<location on ftp.sec.gov>

    NOTE: to abide by the rules of the
    `SEC FTP site <https://www.sec.gov/edgar/searchedgar/ftpusers.htm>`_ you will need to
    include your email for logging in.  This only seems to be used if there is a problem
    with the server. You can set your email in config.py.

    Args:
        years (Iterable): One item for each year.  Defaults to entire history available
            through current year.
        output_dir (str): Directory for output. Defaults to 'data/form_index'.
        overwrite: If True, each delimited file will be deleted before writing to it, otherwise
            they are appended to.  Defaults to False.
        form_types (Iterable): Form types to ingest. For insider trading activity these are
            forms 3, 4, 5, as described on the `SEC forms site <https://www.sec.gov/forms>`_.
        output_delimiter (char): Single character delimiter (as required by python's csv package).
            Defaults to '|'.
        email (str): Your email address used for logging into SEC ftp site. Defaults to value
            in config.py.

    """
    ftp = FTP('ftp.sec.gov')
    # login and password, as per instructions on SEC ftp site
    # https://www.sec.gov/edgar/searchedgar/ftpusers.htm
    login = 'anonymous'
    password = email
    ftp.login(login, password)
    for year in years:
        output_path = os.path.join(output_dir, '{}.csv'.format(year))
        if overwrite is True:
            utils.silentremove(output_path)
        folders = ftp.nlst('/edgar/full-index/{YYYY}'.format(YYYY=year))
        quarters = [folder for folder in folders if 'QTR' in folder]
        for quarter in quarters:
            # zipfile acts as a file, but is held in memory as opposed to saving to a file
            zipfile = StringIO()
            index_loc = '{quarter}/form.gz'.format(quarter=quarter)
            # write the compressed gzip file to zipfile
            ftp.retrbinary('RETR {}'.format(index_loc), zipfile.write)
            zipfile.seek(0)
            # input_src is the uncompressed version of zipfile
            input_src = gzip.GzipFile(mode='rb', fileobj=zipfile)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            write_forms_index(input_src, output_path=output_path, form_types=form_types,
                              output_delimiter=output_delimiter)
            input_src.close()
    ftp.quit()


def _get_sec_form_cache(form_loc):
    """Retrieves saved form of saved SEC form"""
    fpath = os.path.join(config.FORM_CACHE_DIR, form_loc)
    text = utils.read_file(fpath)
    return text


def _save_sec_form_cache(form_loc, text):
    """Saves contents of SEC form"""
    outpath = os.path.join(config.FORM_CACHE_DIR, form_loc)
    utils.makedirs(os.path.dirname(outpath))
    utils.save_file(outpath, text, compress=True)


def download_sec_form(form_loc):
    """Downloads SEC form from EDGAR system using HTTPS"""
    url = config.EDGAR_BASEURL + form_loc
    r = requests.get(url)
    content = r.content
    return content


def get_sec_form(form_loc, cache_file=False):
    """
    Retrieves an SEC form from location using cache or HTTPS

    Args:
        form_loc (str): Location of form on SEC's EDGAR site.
            Example: 'edgar/data/1551138/0001144204-16-074214.txt'

    Returns:
        string
    """
    try:
        text = _get_sec_form_cache(form_loc)
        used_cache = True
    except FileNotFoundError:
        content = download_sec_form(form_loc)
        text = content.decode('utf8')
        used_cache = False
        if cache_file is True:
            _save_sec_form_cache(form_loc, content)
    return text, used_cache
