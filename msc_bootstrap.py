#!/usr/bin/python
import subprocess
import json
import simplejson
import sys
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
            used_outputs=[]
            outputs_sum=0
            # to divide the dacoins between the addresses, we check how much contributed each
            for i in json_tx['inputs']:
                prev_tx_hash=i['previous_output'].split(':')[0]
                prev_tx_output_index=i['previous_output'].split(':')[1]
                json_prev_tx=get_tx(prev_tx_hash)
                output_value=json_prev_tx['outputs'][int(prev_tx_output_index)]['value']
                # calculate sum of outputs
                outputs_sum += output_value
                used_outputs.append((i['address'],str(output_value)))
            amount_of_outputs=len(used_outputs)
            output_number=1
            accomulated_outputs=0
            # output info about the tx generally
            output_per_tx(output_format, block, tx_hash, value, dacoins)
            for outputs in used_outputs:
                address=outputs[0]
                output_value=int(outputs[1])
                if output_number == amount_of_outputs:
                    # to make sure the sum is as expected and avoid rounding errors
                    output_value=outputs_sum-accomulated_outputs
                else:
                    output_value=int(outputs[1])
                    accomulated_outputs+=output_value
                    output_number+=1
                # output per address - each one gets its proportional share
                output_per_address(output_format, address, output_value, dacoins, outputs_sum)


if __name__ == "__main__":
        main()
