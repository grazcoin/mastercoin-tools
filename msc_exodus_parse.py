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

import operator
from optparse import OptionParser
from msc_utils_parsing import *

# global last block on the net
last_height=get_last_height()

mint2b_addr='3Mint2B5ECNdXDZJneJ1XtKmrkmnMbwBbN'
default_currencies_dict={'MSC':{'exodus': '1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P', 'currency_id':1, 'name':'Mastercoin'},'TMSC':{'exodus': '1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P', 'currency_id':2, 'name':'Test Mastercoin'},'BTC':{'exodus':'','currency_id':0,'name':'Bitcoin'}}

def mint2b_parse():

    ######################################
    # reading and setting options values #
    ######################################

    msc_globals.init()

    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")
    parser.add_option("-s", "--start-block",dest='starting_block_height',default=None,
                        help="start the parsing at a specific block height (default is last)")
    parser.add_option( "-r", "--repository-path", dest='repository_path', default="~/mastercoin-tools", 
                        help="Specify the location of the mastercoin-tools repository (defaults to ~/mastercoin-tools" )

    (options, args) = parser.parse_args()
    msc_globals.d=options.debug_mode
    requested_block_height=options.starting_block_height

    # show debug on
    if msc_globals.d:
        debug('debug is on')


    # get last updated currencies dict
    extracted_currencies_dict=load_dict_from_file('general/extracted_currencies.json', skip_error=True)
    if extracted_currencies_dict == {}:
        extracted_currencies_dict = default_currencies_dict

    if requested_block_height != None:
        starting_block_height=requested_block_height
    else:
        starting_block_height=290000

    # to catch chain reorgs, check 5 blocks back
    starting_block_height = int(starting_block_height) - 5

    info('starting parsing '+mint2b_addr+' at block '+str(starting_block_height))

    msc_globals.exodus_scan=mint2b_addr

    # get all tx of exodus address
    history=get_history(msc_globals.exodus_scan)
    history.sort(key=output_height)

    ###########################
    ### parsing starts here ###
    ###########################

    # go over transaction from all history of exodus address
    last_block=0
    for tx_dict in history:
	value=tx_dict['value']
	if starting_block_height != None:
	    current_block=tx_dict['output_height']
	    if current_block != 'Pending':
		if int(current_block)<int(starting_block_height):
		    debug('skip block '+str(current_block)+' since starting at '+str(starting_block_height))
		    continue
	    else:
		# Pending block will be checked whenever they are not Pending anymore.
		continue
	try:
	    tx_hash=tx_dict['output'].split(':')[0]
	    tx_output_index=tx_dict['output'].split(':')[1]
	except KeyError, IndexError:
	    error("Cannot parse tx_dict:" + str(tx_dict))
	raw_tx=get_raw_tx(tx_hash)
	json_tx=get_json_tx(raw_tx, tx_hash)
	if json_tx == None:
	    error('failed getting json_tx (None) for '+tx_hash)
	(block,index)=get_tx_index(tx_hash)
	if block == None or block == "failed:" or index == None:
	    error('failed getting block None or index None for '+tx_hash)
	if last_block < int(block):
	    last_block = int(block)

	outputs_list=json_tx['outputs']
	(outputs_list_no_exodus, outputs_to_exodus, different_outputs_values, invalid)=examine_outputs(outputs_list, tx_hash, raw_tx)

	if invalid != None:
	    info(str(invalid[1])+' on '+tx_hash)
	    parsed['invalid']=invalid

	num_of_outputs=len(outputs_list)

	(block_timestamp, err)=get_block_timestamp(int(block))
	if block_timestamp == None:
	    error('failed getting block timestamp of '+str(block)+': '+err)

	parsed=parse_mint(raw_tx, tx_hash)
	parsed['method']='mint'
	parsed['block']=str(block)
	parsed['index']=str(index)
	if not parsed.has_key('invalid'):
	    parsed['invalid']=False
	parsed['tx_time']=str(block_timestamp)+'000'
	debug(str(parsed))
	filename='tx/'+parsed['tx_hash']+'.json'
	orig_json=None
	try:
	    #debug(str(parsed))
	    filename='tx/'+parsed['tx_hash']+'.json'
	    atomic_json_dump(parsed, filename)
	except IOError:
	    info('failed writing mint tx '+tx_hash)

        # add to extracted currencies dict
        issuer_exodus='unknown'
        try:
            issuer_exodus=parsed['to_address']
        except KeyError:
            info('cannot find issuer exodus on '+tx_hash)

        (extracted,symbol)=extract_name(issuer_exodus)
        if not extracted:
            info('failed extracting name for '+issuer_exodus)
        test_symbol='T'+symbol
        if not extracted_currencies_dict.has_key(symbol):
            currency_details_dict={'exodus':issuer_exodus,'currency_id':1,'name':symbol+' coin'}
            extracted_currencies_dict[symbol]=currency_details_dict
            currency_details_dict={'exodus':issuer_exodus,'currency_id':2,'name':'Test '+symbol+' coin'}
            extracted_currencies_dict[test_symbol]=currency_details_dict

        debug(extracted_currencies_dict)
        atomic_json_dump(extracted_currencies_dict, 'general/extracted_currencies.json', add_brackets=True)

if __name__ == "__main__":
    mint2b_parse()
