import re
from ftplib import FTP
from StringIO import StringIO

from lxml import etree

def get_sec_form(form_loc):
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
    return re.search('<XML>((.|\n)*?)<\/XML>', form).groups()[0].strip()

def get_transaction_dict(transaction_element):
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
    issuer_dict = {}
    issuer_dict['cik'] = issuer_element.xpath('.//issuerCik')[0].text
    issuer_dict['name'] = issuer_element.xpath('.//issuerName')[0].text
    issuer_dict['symbol'] = issuer_element.xpath('.//issuerTradingSymbol')[0].text
    return issuer_dict

def get_trade_holdings_dict(holding_element):
    holdings_dict = {}
    assert(len(holding_element.xpath('./securityTitle/value'))==1)
    holdings_dict['sec_type'] = holding_element.xpath('./securityTitle/value')[0].text
    assert(len(holding_element.xpath('.//sharesOwnedFollowingTransaction/value'))==1)
    holdings_dict['shares_owned_after'] = holding_element.xpath('.//sharesOwnedFollowingTransaction/value')[0].text
    holdings_dict['direct_or_indirect'] = holding_element.xpath('.//directOrIndirectOwnership/value')[0].text
    return holdings_dict

def get_form_dict(form_loc):
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
