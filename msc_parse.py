#!/usr/bin/python
import subprocess
import json
import simplejson
import sys
import operator
from msc_utils import *

debug=False

def main():

    if debug!=True:
        # get all tx of exodus address
        history=get_history(exodus_address)
        history.sort(key=output_height)
    else:
        t1={"output": "63c7eb7032645344a362bf729fb05217156d6d5d7e610e4e1953485dd1892d1c:0",
        "output_height": 252317,
        "value":  "60000"}
        history=[]
        history.append(t1)

    # go over transaction from all history of 1EXoDus address
    for tx_dict in history:
        block=tx_dict['output_height']
        value=tx_dict['value']
        try:
            tx_hash=tx_dict['output'].split(':')[0]
            tx_output_index=tx_dict['output'].split(':')[1]
        except KeyError, IndexError:
            error("Cannot parse tx_dict:" + str(tx_dict))
        raw_tx=get_raw_tx(tx_hash)
        json_tx=get_json_tx(raw_tx, tx_hash)
        # examine the outputs
        outputs_list=json_tx['outputs']
        # if we're here, then 1EXoDus is within the outputs. Remove it, but ...
        outputs_list_no_exodus=[]
        outputs_to_exodus=[]
        for o in outputs_list:
            if o['address']!=exodus_address:
                outputs_list_no_exodus.append(o)
            else:
                outputs_to_exodus.append(o)
        # take care if multiple 1EXoDus exist (for the case that someone sends msc
        # to 1EXoDus, or have 1EXoDus as change address)
        if len(outputs_to_exodus) != 1:
            # add all but the marker outputs
            error("not implemented tx with multiple 1EXoDus outputs: "+tx_hash)

        num_of_outputs=len(outputs_list)
        if num_of_outputs > 2: # for reference, data, marker
            try:
                # collect all "from addresses" (normally only a single one)
                from_address=''
                inputs=json_tx['inputs']
                for i in inputs:
                    if from_address != '':
                        from_address+=';'
                    from_address+=i['address']

                # sort outputs according to dataSequenceNum to find the reference (n) and data (n+1)
                outputs_list_no_exodus.sort(key=get_dataSequenceNum)
                # look for sequence of at least length 2 to find the reference address
                seq_list=[]
                for o in outputs_list_no_exodus:
                    seq=get_dataSequenceNum(o)
                    seq_list.append(int(seq,16))
                reference=None
                data=None
                # currently support only the simple send (a single data packet)
                for s in seq_list:
                    if (s+1)%256 == int(seq_list[(seq_list.index(s)+1)%len(seq_list)]):
                        data=outputs_list_no_exodus[seq_list.index(s)]
                        reference=outputs_list_no_exodus[(seq_list.index(s)+1)%len(seq_list)]
                # FIXME sanity checks:
                # verify that all follow (n+1) mod 256 dataSequenceNum rule
                # verify not more than 255 data
                to_address=reference['address']
                data_script=data['script'].split()[3].zfill(42)
                baseCoin=data_script[0:2] # 00 for normal bitcoin (different for multisig?)
                dataSequenceNum=data_script[2:4]
                transactionType=data_script[4:12]
                currencyId=data_script[12:20]
                amount=data_script[20:36]
                padding=data_script[36:42]
                # FIXME: checksum?
                print tx_hash+','+from_address+','+to_address+','+str(int(amount,16)/100000000.0)+','+\
                        get_currency_type(currencyId)+','+get_transaction_type(transactionType)
            except KeyError, IndexError:
                info('invalid mastercoin tx '+tx_hash)
        else:
            #info('not enough inputs in tx: '+tx_hash)
            pass

if __name__ == "__main__":
    main()
