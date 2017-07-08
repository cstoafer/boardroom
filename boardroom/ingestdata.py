import os
from ftplib import FTP
try:
    from StringIO import StringIO
except:
    from io import StringIO, BytesIO
import gzip
import csv
import datetime

import requests
from bs4 import BeautifulSoup

from boardroom import utils
from boardroom import config

def ticker_to_cik(ticker, use_cache=True):
    '''
    Returns a company's CIK with their ticker symbol as input.

    The CIK (Central Index Key) is used by the SEC for data lookup for company.

    Args:
        ticker (str): company stock ticker symbol

    Examples:
        >>> ticker_to_cik('KO')
        u'0000021344'

    Returns:
        Unicode: CIK (Central Index Key) for company.
    '''
    if not isinstance(ticker, basestring):
        raise TypeError('ticker needs to be a string')
    if use_cache:
        ticker_cik_dict = utils.load_cache_dict('ticker_cik.p')
        if ticker in ticker_cik_dict:
            return ticker_cik_dict[ticker]
    query = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&' \
            'CIK={}&count=100&output=xml'.format(ticker)
    r = requests.get(query)
    xml = r.text
    soup = BeautifulSoup(xml, "html.parser")
    cik = soup.find('cik').decode_contents()
    # if use_cache is True, then add the data to the cached dictionary
    if use_cache:
        ticker_cik_dict[ticker] = cik
        utils.save_cache_dict(ticker_cik_dict, 'ticker_cik.p')
    return cik

def write_forms_index(input_src, output_path, form_types=['4'], output_delimiter='|'):
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
                    output_dir='data/form_index/', overwrite=False, form_types=['4'],
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
            input_src = gzip.GzipFile(mode = 'rb', fileobj = zipfile)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            write_forms_index(input_src, output_path=output_path, form_types=form_types,
                              output_delimiter=output_delimiter)
            input_src.close()
    ftp.quit()


