import re
from ftplib import FTP
from StringIO import StringIO

from lxml import etree

def get_sec_form(form_loc):
    '''
    Retrieves an SEC form from location using FTP site.

    Args:
        form_loc (str): Location of form on SEC's FTP site.
            Example: 'edgar/data/1551138/0001144204-16-074214.txt'

    Returns:
        StringIO
    '''
    ftp = FTP('ftp.sec.gov')
    # login and password, as per instructions on SEC ftp site
    # https://www.sec.gov/edgar/searchedgar/ftpusers.htm
    login = 'anonymous'
    password = 'cstoafer@gmail.com' #email
    ftp.login(login, password)
    formfile = StringIO()
    _ = ftp.retrbinary('RETR {}'.format(form_loc), formfile.write)
    return formfile

def get_xml(form):
    '''
    Parses out XML section of file within tag <XML>...</XML>
    '''
    return re.search('<XML>((.|\n)*?)<\/XML>', form).groups()[0].strip()

def get_trade_holdings_dict(holding_element):
    '''
    Returns dictionary with data values for trade holdings contained in the xml of the SEC form.

    Args:
        holding_element: lxml element (e.g. result of xpath search) of security holdings data.

    Returns:
        dict: with security holdings data information keys
            sec_type: Type of security (e.g. Common Stock)
            shares_owned_after: Number of shares owners owns after transaction
            direct_or_indirect: Whether the owner owned the shares directly or indirectly
    '''
    holdings_dict = {}
    assert(len(holding_element.xpath('./securityTitle/value'))==1)
    holdings_dict['sec_type'] = holding_element.xpath('./securityTitle/value')[0].text
    assert(len(holding_element.xpath('.//sharesOwnedFollowingTransaction/value'))==1)
    holdings_dict['shares_owned_after'] = holding_element.xpath('.//sharesOwnedFollowingTransaction/value')[0].text
    holdings_dict['direct_or_indirect'] = holding_element.xpath('.//directOrIndirectOwnership/value')[0].text
    return holdings_dict

def get_transaction_dict(transaction_element):
    '''
    Returns dictionary with data values contained in the xml of the SEC form.

    Args:
        transaction_element: lxml element (e.g. result of xpath search) of transaction data.

    Returns:
        dict: with transaction data information keys
            sec_type: Type of security (e.g. Common Stock)
            date: Date of transaction
            transaction_code
            num_shares
            price_per_share
            acquired_disposed_code: Whether shares were acquired or disposed
            shares_owned_after: Number of shares owners owns after transaction
            direct_or_indirect: Whether the owner owned the shares directly or indirectly
    '''
    transaction_dict = {}
    transaction_dict['sec_type'] = transaction_element.xpath('./securityTitle/value')[0].text
    transaction_dict['date'] = transaction_element.xpath('./transactionDate/value')[0].text
    transaction_dict['transaction_code'] = transaction_element.xpath('.//transactionCode')[0].text
    transaction_dict['num_shares'] = transaction_element.xpath('.//transactionShares/value')[0].text
    transaction_dict['price_per_share'] = transaction_element.xpath('.//transactionPricePerShare/value')[0].text
    transaction_dict['acquired_disposed_code'] = transaction_element.xpath('.//transactionAcquiredDisposedCode/value')[0].text
    transaction_dict['shares_owned_after'] = transaction_element.xpath('.//sharesOwnedFollowingTransaction/value')[0].text
    transaction_dict['direct_or_indirect'] = transaction_element.xpath('.//directOrIndirectOwnership/value')[0].text
    return transaction_dict

def get_owner_dict(owner_element):
    '''
    Returns dictionary with data values for the owners contained in the xml of the SEC form.

    Args:
        owner_element: lxml element (e.g. result of xpath search) of security owner data.

    Returns:
        dict: with security owner data information keys
            cik: CIK (SEC ID) of owner
            name: Name of owner
            addr1: Street address line 1
            addr2: Street address line 2
            city
            state
            zipcode
            is_director: 1 if owner is a director of company in transaction, else 0
            is_officer: 1 if owner is an office of company in transaction, else 0
            is_ten_percent_owner: 1 if owner owns 10% of company in transaction, else 0
            is_other: 1 if owner is affiliated in another way with company in transaction, else 0
    '''
    owner_dict = {}
    owner_dict['cik'] = owner_element.xpath('.//rptOwnerCik')[0].text
    owner_dict['name'] = owner_element.xpath('.//rptOwnerName')[0].text
    owner_dict['addr1'] = owner_element.xpath('.//rptOwnerStreet1')[0].text
    owner_dict['addr2'] = owner_element.xpath('.//rptOwnerStreet2')[0].text
    owner_dict['city'] = owner_element.xpath('.//rptOwnerCity')[0].text
    owner_dict['state'] = owner_element.xpath('.//rptOwnerState')[0].text
    owner_dict['zipcode'] = owner_element.xpath('.//rptOwnerZipCode')[0].text
    owner_dict['is_director'] = owner_element.xpath('.//isDirector')[0].text
    owner_dict['is_officer'] = owner_element.xpath('.//isOfficer')[0].text
    owner_dict['is_ten_percent_owner'] = owner_element.xpath('.//isTenPercentOwner')[0].text
    owner_dict['is_other'] = owner_element.xpath('.//isOther')[0].text
    return owner_dict

def get_issuer_dict(issuer_element):
    '''
    Returns dictionary with data values for the issuer contained in the xml of the SEC form.

    Args:
        issuer_element: lxml element (e.g. result of xpath search) of issuer data.

    Returns:
        dict: with issuer data information keys
            cik: CIK (SEC ID) of issuer
            name: Name of issuer
            symbol: Trading symbol of issuer
    '''
    issuer_dict = {}
    issuer_dict['cik'] = issuer_element.xpath('.//issuerCik')[0].text
    issuer_dict['name'] = issuer_element.xpath('.//issuerName')[0].text
    issuer_dict['symbol'] = issuer_element.xpath('.//issuerTradingSymbol')[0].text
    return issuer_dict

def get_form_dict(form_loc):
    '''
    Returns dictionary with data values contained in the xml of the SEC form.

    Contains data for issuer, owners, and transactions.

    Args:
        form_loc (str): Location of form on SEC's FTP site.
            Example: 'edgar/data/1551138/0001144204-16-074214.txt'

    Returns:
        dict: with data for issuer, owners, and transactions in SEC form.
            issuer: Issuer of form
            owners: Owners of securities that were traded
            trades: Transaction data for trades
    '''
    formfile = get_sec_form(form_loc)
    formfile.seek(0)
    xmlcontent = get_xml(formfile.read())
    tree = etree.fromstring(xmlcontent)
    schema_version = tree.xpath('//schemaVersion')[0].text
    # Eventually support for forms 3,4,5
    form_type = tree.xpath('//documentType')[0].text
    owners = tree.xpath('//reportingOwner')
    issuers = tree.xpath('//issuer')
    issuer_dict_all = {}
    owner_dict_all = {}
    for issuer in issuers:
        issuer_dict = get_issuer_dict(issuer)
        issuer_dict_all[issuer_dict['cik']] = issuer_dict
    for owner in owners:
        owner_dict = get_owner_dict(owner)
        owner_dict_all[owner_dict['cik']] = owner_dict
    trade_info_dict = {}
    trade_info = tree.xpath('//nonDerivativeTable')
    assert(len(trade_info)==1)
    trade_holdings = trade_info[0].xpath('.//nonDerivativeHolding')
    assert(len(trade_holdings)==1)
    trade_holdings_dict = get_trade_holdings_dict(trade_holdings[0])
    trade_transactions = trade_info[0].xpath('.//nonDerivativeTransaction')
    transactions_all = []
    for transaction in trade_transactions:
        transaction_dict = get_transaction_dict(transaction)
        transactions_all.append(transaction_dict)
    trade_info_dict['holdings'] = trade_holdings_dict
    trade_info_dict['transactions'] = transactions_all
    form_dict = {
        'issuer': issuer_dict_all,
        'owners': owner_dict_all,
        'trades': trade_info_dict
        }
    return form_dict
