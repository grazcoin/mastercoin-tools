#!/usr/bin/python

#######################################################
#                                                     #
#  Copyright Masterchain Grazcoin Grimentz 2013-2014  #
#  https://github.com/grazcoin/mastercoin-tools       #
#  https://masterchain.info                           #
#  masterchain@@bitmessage.ch                         #
#  License AGPLv3                                     #
#                                                     #
#######################################################

import os
import urllib2
from optparse import OptionParser
from msc_utils_validating import *

##################################
# main function - updates prices #
##################################
def update_prices():

    # parse command line arguments
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")

    (options, args) = parser.parse_args()
    msc_globals.init()
    msc_globals.d=options.debug_mode

    info('starting update prices')

    filename='general/bitcoinaverage_ticker_usd.json'
    response = urllib2.urlopen('https://api.bitcoinaverage.com/ticker/USD/')
    f = open(filename, "w")
    f.write(response.read())
    f.close()
    l=load_dict_from_file(filename, all_list=True)
    bitcoin_avg=l['24h_avg']

    filename='general/masterxchange_trades.json'
    response = urllib2.urlopen('https://masterxchange.com/api/trades.php')
    f = open(filename, "w")
    f.write(response.read())
    f.close()
    l=load_dict_from_file(filename, all_list=True)
    total_paid=0
    total_amount=0
    for trade in l:
        price=float(trade['price'])
        amount=float(trade['amount'])
        total_paid+=price*amount
        total_amount+=amount

    mastercoin_avg=total_paid/total_amount

    msc_dict={"ID":"1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P-0","name":"Mastercoin","symbol":"MSC", "dollar":mastercoin_avg*bitcoin_avg}
    tmsc_dict={"ID":"1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P-1","name":"Test Mastercoin","symbol":"TMSC","dollar":"0.0"}
    bitcoin_dict={"ID":"Bitcoin","name":"Bitcoin","symbol":"BTC","dollar":bitcoin_avg}

    currencies_list=[msc_dict,tmsc_dict,bitcoin_dict]
    atomic_json_dump(currencies_list,'www/currencies.json', add_brackets=False)

    info('update prices done')

if __name__ == "__main__":
    update_prices()
