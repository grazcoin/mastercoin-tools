#!/usr/bin/python
import subprocess
import json
import simplejson
import sys
import operator
from msc_utils import *

first_exodus_bootstrap_block=249498
last_exodus_bootstrap_block=255365
exodus_bootstrap_deadline=1377993600

def main():

    # full story format or just csv
    output_format='csv'
    if len(sys.argv) > 1:
        if sys.argv[1]=='story':
            output_format='story' # a.k.a long format
    # get all tx of exodus address
    history=get_history("1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P")
    # sort
    history.sort(key=output_height)
    # parse result checking for exodus bootstrap entries
    for tx_dict in history:
        block=tx_dict['output_height']
        value=tx_dict['value']
        try:
            tx_hash=tx_dict['output'].split(':')[0]
            tx_output_index=tx_dict['output'].split(':')[1]
        except KeyError, IndexError:
            error("Cannot parse tx_dict:" + str(tx_dict))

        # interesting addresses are only those within exodus bootstrap blocks
        if int(block) >= first_exodus_bootstrap_block and int(block) <= last_exodus_bootstrap_block:
            tx_sec_before_deadline=exodus_bootstrap_deadline-get_block_timestamp(int(block))
            # bonus is 10% for a week
            bonus=max((tx_sec_before_deadline+0.0)/(3600*24*7*10.0)*100,0)
            dacoins=str('{:.0f}'.format(int(value)*(100+bonus)))
            json_tx=get_tx(tx_hash)
            # give dacoins to highest contributing address.
            output_dict={} # dict to collect outputs per address
            for i in json_tx['inputs']:
                prev_tx_hash=i['previous_output'].split(':')[0]
                prev_tx_output_index=i['previous_output'].split(':')[1]
                json_prev_tx=get_tx(prev_tx_hash)
                output_value=json_prev_tx['outputs'][int(prev_tx_output_index)]['value']
                if output_dict.has_key(i['address']):
                    output_dict[i['address']]+=output_value
                else:
                    output_dict[i['address']]=output_value
            # the winning address is the one with highest contributions
            address=max(output_dict.iteritems(), key=operator.itemgetter(1))[0]
            # output info about the tx generally
            output_per_tx(output_format, block, tx_hash, value, dacoins)
            # output per address
            output_per_address(output_format, address, dacoins)


if __name__ == "__main__":
        main()
