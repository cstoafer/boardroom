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

def _get_single_xml_element(element, xpath_str):
    '''
    Performs xpath search and expects one element.
    '''
    value_list = element.xpath(xpath_str)
    if len(value_list) == 0:
        raise ValueError('There are no elements of type {} in the element {}'.format(xpath_str,
                                                                                    element))
    if len(value_list) > 1:
        raise ValueError('Only 1 value was expected in\n'
                         'xpath: {}\n'
                         'element: {}\n'
                         'but more were returned'.format(xpath_str, element))
    return value_list[0]

def _get_single_xml_value(element, xpath_str):
    '''
    Gets a single value from xml.
    '''
    return _get_single_xml_element(element, xpath_str).text

def _xpath_to_value_mapping(element, mapping):
    '''
    Returns a dict with the keys from ``mapping`` and values of the parsed xml.

    Args:
        element: lxml element for performing xpath.
        mapping: dictionary mapping data keys to xpath strings.

    Returns:
        dict: mapping keys from ``mapping`` to the values retrieved from parsing the xml in
            ``element``.
    '''
    parsed_dict = {}
    for key, xpath_str in mapping.iteritems():
        parsed_dict[key] = _get_single_xml_value(element, xpath_str)
    return parsed_dict

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
    mapping = {
            'sec_type':             './securityTitle/value',
            'shares_owned_after':   './/sharesOwnedFollowingTransaction/value',
            'direct_or_indirect':   './/directOrIndirectOwnership/value'
            }
    return _xpath_to_value_mapping(holding_element, mapping)

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
    mapping = {
            'sec_type':                 './securityTitle/value',
            'date':                     './transactionDate/value',
            'transaction_code':         './/transactionCode',
            'num_shares':               './/transactionShares/value',
            'price_per_share':          './/transactionPricePerShare/value',
            'acquired_disposed_code':   './/transactionAcquiredDisposedCode/value',
            'shares_owned_after':       './/sharesOwnedFollowingTransaction/value',
            'direct_or_indirect':       './/directOrIndirectOwnership/value'
            }
    return _xpath_to_value_mapping(transaction_element, mapping)

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
    mapping = {
            'cik':                      './/rptOwnerCik',
            'name':                     './/rptOwnerName',
            'addr1':                    './/rptOwnerStreet1',
            'addr2':                    './/rptOwnerStreet2',
            'city':                     './/rptOwnerCity',
            'state':                    './/rptOwnerState',
            'zipcode':                  './/rptOwnerZipCode',
            'is_director':              './/isDirector',
            'is_officer':               './/isOfficer',
            'is_ten_percent_owner':     './/isTenPercentOwner',
            'is_other':                 './/isOther'
            }
    return _xpath_to_value_mapping(owner_element, mapping)

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
    mapping = {
            'cik':      './/issuerCik',
            'name':     './/issuerName',
            'symbol':   './/issuerTradingSymbol'
            }
    return _xpath_to_value_mapping(issuer_element, mapping)

def get_issuer_dict_from_xmltree(tree):
    '''
    Parses issuer information from SEC Filing xml
    '''
    issuers = tree.xpath('//issuer')
    issuer_dict_all = {}
    for issuer in issuers:
        issuer_dict = get_issuer_dict(issuer)
        issuer_dict_all[issuer_dict['cik']] = issuer_dict
    return issuer_dict_all

def get_owner_dict_from_xmltree(tree):
    '''
    Parses security owner information from SEC Filing xml
    '''
    owners = tree.xpath('//reportingOwner')
    owner_dict_all = {}
    for owner in owners:
        owner_dict = get_owner_dict(owner)
        owner_dict_all[owner_dict['cik']] = owner_dict
    return owner_dict_all

def get_trade_info_dict_from_xmltree(tree):
    '''
    Parses transaction trade information from SEC Filing xml
    '''
    trade_info_dict = {}
    trade_info = _get_single_xml_element(tree, '//nonDerivativeTable')
    trade_holdings = _get_single_xml_element(trade_info, '//nonDerivativeHolding')
    trade_holdings_dict = get_trade_holdings_dict(trade_holdings)
    trade_transactions = trade_info.xpath('.//nonDerivativeTransaction')
    transactions_all = []
    for transaction in trade_transactions:
        transaction_dict = get_transaction_dict(transaction)
        transactions_all.append(transaction_dict)
    trade_info_dict['holdings'] = trade_holdings_dict
    trade_info_dict['transactions'] = transactions_all
    return trade_info_dict

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
    form_dict = {
        'issuer': get_issuer_dict_from_xmltree(tree),
        'owners': get_owner_dict_from_xmltree(tree),
        'trades': get_trade_owner_dict_from_xmltree(tree)
        }
    return form_dict
