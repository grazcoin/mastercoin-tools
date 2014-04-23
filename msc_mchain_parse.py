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

def mchain_parse():

    ######################################
    # reading and setting options values #
    ######################################

    msc_globals.init()

    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")
    parser.add_option( "-r", "--repository-path", dest='repository_path', default="~/mastercoin-tools", 
                        help="Specify the location of the mastercoin-tools repository (defaults to ~/mastercoin-tools" )

    (options, args) = parser.parse_args()
    msc_globals.d=options.debug_mode

    # show debug on
    if msc_globals.d:
        debug('debug is on')


    # get last updated currencies dict
    mchain_donors_list=[]

    starting_block_height=290000

    info('collect donors to '+mchain_addr+' at block '+str(starting_block_height))

    history=get_history(mchain_addr)
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

	inputs_list=json_tx['inputs']
        try:
            donor_address = inputs_list[0]['address']
            mchain_donors_list.append({'address':donor_address, 'value':value, 'block':block})
        except KeyError:
            info('problem with donor tx '+tx_hash)

    info(mchain_donors_list)
    atomic_json_dump(mchain_donors_list, 'general/mchain_donors.json', add_brackets=True)

if __name__ == "__main__":
    mchain_parse()
