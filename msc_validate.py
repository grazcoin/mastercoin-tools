#!/usr/bin/python
import subprocess
import json
import simplejson
import sys
import operator
import time
import os
from optparse import OptionParser
from msc_utils import *

d=False # debug_mode

def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

def main():
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")

    (options, args) = parser.parse_args()
    d=options.debug_mode

    # run on all files in tx
    tx_files=sorted_ls('tx')

    # load dict of each
    tx_list=[]
    for filename in tx_files:
        if filename.endswith('.json'):
            f=open('tx/'+filename)
	    tx_list.append(json.load(f)[0])
            f.close()
    # sort according to time
    sorted_tx_list = sorted(tx_list, key=lambda k: (k['block'],k['index'])) 

    # create address dict and update balance of valid tx
    addr_dict={}
    for t in sorted_tx_list:
        try:
            if t['invalid']!=True:
                to_addr=t['to_address']
                from_addr=t['from_address']
                amount_transfer=to_satoshi(t['formatted_amount'])
                currency=t['currency_str']
                tx_hash=t['tx_hash']
                tx_list_for_addr=[]
                if from_addr == 'exodus':
                    # exodus purchase
                    if not addr_dict.has_key(to_addr):
                                             #msc balance    #received   #sent   #in  #out #exodus
                        addr_dict[to_addr]=([amount_transfer,0,          0,      [],  [],  [t]],
                        #test msc balance         #received  #sent   #in  #out #exodus # exodus purchase
				[amount_transfer, 0,         0,      [],  [],  [t]],   [amount_transfer])
                    else:
                        addr_dict[to_addr][0][0]+=amount_transfer # msc
                        addr_dict[to_addr][1][0]+=amount_transfer # test msc
                        addr_dict[to_addr][0][5].append(t)        # incoming msc
                        addr_dict[to_addr][1][5].append(t)        # incoming test msc
                        addr_dict[to_addr][2][0]+=amount_transfer # exodus purchase
                    # exodus bonus - 10% for exodus (available slowly during the years)
                    if not addr_dict.has_key(exodus_address):
                        ten_percent=(amount_transfer+5)/10
                        addr_dict[exodus_address]=([ten_percent,0,0,[],[],[t]],[ten_percent,0,0,[],[],[t]],[0])
                    else:
                        addr_dict[exodus_address][0][0]+=ten_percent # msc
                        addr_dict[exodus_address][1][0]+=ten_percent # test msc
                        addr_dict[exodus_address][0][5].append(t)    # incoming msc
                        addr_dict[exodus_address][1][5].append(t)    # incoming test msc
                        addr_dict[exodus_address][2][0]+=0           # no accounting for exodus 10% due to purchase
                else:
                    # normal transfer
                    if not addr_dict.has_key(from_addr):
                        info('try to pay from non existing address at '+tx_hash)
                        # mark tx as invalid and continue
                    else:
                        if currency=='Mastercoin':
                            c=0
                        else:
                            if currency=='Test Mastercoin':
                                c=1
                            else:
                                info('unknown currency '+currency)
                                continue
                        balance_from=addr_dict[from_addr][c][0]
                        if amount_transfer > int(balance_from):
                            info('balance of '+currency+' is too low on '+tx_hash)
                            # mark tx as invalid and continue
                        else:
                            # update to_addr
                            if not addr_dict.has_key(to_addr):
                                if c==0:                #msc          #int #out  #test msc #in #out
                                    addr_dict[to_addr]=([amount_transfer,amount_transfer,0,[t],[],[]],[0,0,0,[],[],[]],[0])
                                else:
                                    addr_dict[to_addr]=([0,0,0,[],[],[]],[amount_transfer,amount_transfer,0,[t],[],[]],[0])
                            else:
                                if c==0:
                                    addr_dict[to_addr][0][0]+=amount_transfer # msc
                                    addr_dict[to_addr][0][1]+=amount_transfer # msc total received
                                    addr_dict[to_addr][0][3].append(t)        # incoming msc
                                else:                                    
                                    addr_dict[to_addr][1][0]+=amount_transfer # test msc
                                    addr_dict[to_addr][1][1]+=amount_transfer # test msc total received
                                    addr_dict[to_addr][1][3].append(t)        # incoming test msc
                            # update from_addr
                            if c==0:
                                addr_dict[from_addr][0][0]-=amount_transfer # msc
                                addr_dict[from_addr][0][2]+=amount_transfer # msc total sent
                                addr_dict[from_addr][0][4].append(t)        # incoming msc
                            else:                                    
                                addr_dict[from_addr][1][0]-=amount_transfer # test msc
                                addr_dict[from_addr][1][2]+=amount_transfer # test msc total sent
                                addr_dict[from_addr][1][4].append(t)        # incoming test msc
        except OSError:
            info('error on tx '+t['tx_hash'])

    # create file for each address
    #print addr_dict

    for addr in addr_dict.keys():
        addr_dict_api={}
        addr_dict_api['address']=addr
        addr_dict_api['received_transactions']=addr_dict[addr][0][3]
        addr_dict_api['test_received_transactions']=addr_dict[addr][1][3]
        addr_dict_api['sent_transactions']=addr_dict[addr][0][4]
        addr_dict_api['test_sent_transactions']=addr_dict[addr][0][4]
        addr_dict_api['total_received']=from_satoshi(addr_dict[addr][0][1])
        addr_dict_api['test_total_received']=from_satoshi(addr_dict[addr][1][1])
        addr_dict_api['total_sent']=from_satoshi(addr_dict[addr][0][2])
        addr_dict_api['test_total_sent']=from_satoshi(addr_dict[addr][1][2])
        addr_dict_api['balance']=from_satoshi(addr_dict[addr][0][0])
        addr_dict_api['test_balance']=from_satoshi(addr_dict[addr][1][0])
        addr_dict_api['exodus_transactions']=addr_dict[addr][0][5]
        addr_dict_api['total_exodus']=from_satoshi(addr_dict[addr][2][0])
	
        filename='addr/'+addr+'.json'
        f=open(filename, 'w')
        json.dump(addr_dict_api, f)
        f.close()

if __name__ == "__main__":
    main()
