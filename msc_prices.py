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

    values=load_dict_from_file('www/values.json', all_list=True)
    for entry in values:
        try:
            last_price=float(entry['last_price'])
            symbol=entry['currency']
            coin_name=currencies_per_symbol_dict[symbol]['name']

            updated_prices[coin_name]=last_price*float(bitcoin_avg)
        except KeyError:
            pass

    # prepare updated currency list
    updated_currencies_list=[]
    for coin in coins_list:
        coin_details=currencies_per_name_dict[coin]
        id=coins_dict[coin] # take from pre generated dict
        price=0.0
        try:
            price=updated_prices[coin]
        except KeyError:
            pass
        info('updating '+coin+' with price '+str(price))
        d={"ID":id,"name":coin_details["name"],"symbol":coin_details["symbol"],"dollar":price}
        updated_currencies_list.append(d)

    atomic_json_dump(updated_currencies_list,'www/currencies.json', add_brackets=False)

    info('update prices done')

if __name__ == "__main__":
    update_prices()
