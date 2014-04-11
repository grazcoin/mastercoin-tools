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
    updated_prices={}

    info('starting update prices')

    filename='general/bitcoinaverage_ticker_usd.json'
    response = urllib2.urlopen('https://api.bitcoinaverage.com/ticker/USD/')
    f = open(filename, "w")
    f.write(response.read())
    f.close()
    l=load_dict_from_file(filename, all_list=True)
    bitcoin_avg=l['24h_avg']
    updated_prices['Bitcoin']=bitcoin_avg

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
    updated_prices['Mastercoin']=mastercoin_avg*bitcoin_avg

    # prepare updated currency list
    updated_currencies_list=[]
    for coin in coins_list:
        info('updating '+coin)
        coin_details=currencies_per_name_dict[coin]
        id=coins_dict[coin] # take from pre generated dict
        price=0.0
        try:
            price=updated_prices[coin]
        except KeyError:
            pass
        d={"ID":id,"name":coin_details["name"],"symbol":coin_details["symbol"],"dollar":price}
        updated_currencies_list.append(d)

    atomic_json_dump(updated_currencies_list,'www/currencies.json', add_brackets=False)

    info('update prices done')

if __name__ == "__main__":
    update_prices()
