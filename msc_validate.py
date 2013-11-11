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
            debug(d, filename)
	    tx_list.append(json.load(f)[0])
            try: # for basic which is also exodus
	        tx_list.append(json.load(f)[1])
            except:
                pass
            f.close()
    # sort according to time
    sorted_tx_list = sorted(tx_list, key=lambda k: (k['block'],k['index'])) 

    # prepare lists for mastercoin and test
    sorted_mastercoin_tx_list=[]
    sorted_test_mastercoin_tx_list=[]

    # create address dict and update balance of valid tx
    addr_dict={}
    for t in sorted_tx_list:
        try:
            if t['invalid']==False:

                # update fields icon, details
                try:
                    if t['transactionType']=='00000000':
                        t['icon']='simplesend'
                        t['details']=t['to_address']
                    else:
                        if t['transactionType']=='00000014':
                            t['icon']='selloffer'
                            t['details']=t['formatted_price_per_coin']
                        else:
                            if t['transactionType']=='00000016':
                                t['icon']='sellaccept'
                                t['details']='unknown_price'
                            else:
                               t['icon']='unknown'
                               t['details']='unknown'
                except KeyError as e:
                    # The only *valid* mastercoin tx without transactionType is exodus
                    if t['tx_type_str']=='exodus':
                        t['icon']='exodus'
                        try:
                            t['details']=t['to_address']
                        except KeyError:
                            error('exodus tx with no to_address: '+str(t))
                    else:
                        error('non exodus valid msc tx without '+e+' ('+t['tx_type_str']+') on '+tx_hash)

                to_addr=t['to_address']
                from_addr=t['from_address']
                amount_transfer=to_satoshi(t['formatted_amount'])
                currency=t['currency_str']
                tx_hash=t['tx_hash']
                if from_addr == 'exodus': # assume exodus does not do sell offer/accept
                    # exodus purchase
                    if not addr_dict.has_key(to_addr):
                                             #msc balance    #received   #sent   #b #s #o #in  #out #buy #sold #offer #exodus
                        addr_dict[to_addr]=([amount_transfer,0,          0,      0, 0, 0, [],  [],  [],  [],   [],    [t]],
                                #test msc balance #received  #sent   #b #s #o #in  #out #buy #sold #offer #exodus # exodus purchase
				[amount_transfer, 0,         0,      0, 0, 0, [],  [],  [],  [],   [],    [t]],   [amount_transfer])
                    else:
                        addr_dict[to_addr][0][0]+=amount_transfer # msc
                        addr_dict[to_addr][1][0]+=amount_transfer # test msc
                        addr_dict[to_addr][0][11].append(t)        # incoming msc
                        addr_dict[to_addr][1][11].append(t)        # incoming test msc
                        addr_dict[to_addr][2][0]+=amount_transfer # exodus purchase
                    # exodus bonus - 10% for exodus (available slowly during the years)
                    ten_percent=int((amount_transfer+0.0)/10+0.5)
                    if not addr_dict.has_key(exodus_address):
                        addr_dict[exodus_address]=([ten_percent,0,0,0,0,0,[],[],[],[],[],[t]],[ten_percent,0,0,0,0,0,[],[],[],[],[],[t]],[0])
                    else:
                        addr_dict[exodus_address][0][0]+=ten_percent # 10% bonus msc for exodus
                        addr_dict[exodus_address][1][0]+=ten_percent # 10% bonus test msc for exodus
                        addr_dict[exodus_address][0][11].append(t)    # incoming msc
                        addr_dict[exodus_address][1][11].append(t)    # incoming test msc
                        addr_dict[exodus_address][2][0]+=0           # no accounting for exodus 10% due to purchase
                    # tx belongs to mastercoin and test mastercoin
                    sorted_mastercoin_tx_list.append(t) 
                    sorted_test_mastercoin_tx_list.append(t) 
                else:
                    if currency=='Mastercoin':
                        c=0
                    else:
                        if currency=='Test Mastercoin':
                            c=1
                        else:
                            info('unknown currency '+currency+ ' in tx '+tx_hash)
                            continue
                    # left are normal transfer and sell offer/accept
                    if t['tx_type_str']==transaction_type_dict['00000000']:
                        # the normal transfer case
                        if not addr_dict.has_key(from_addr):
                            info('try to pay from non existing address at '+tx_hash)
                            # mark tx as invalid and continue
                            f=open('tx/'+tx_hash+'.json','r')
                            tmp_dict=json.load(f)[0]
                            f.close()
                            tmp_dict['invalid']=(True,'pay from a non existing address')
                            f=open('tx/'+tx_hash+'.json','w')
                            f.write('[')
                            json.dump(tmp_dict,f)
                            f.write(']\n')
                            f.close()
                        else:
                            balance_from=addr_dict[from_addr][c][0]
                            if amount_transfer > int(balance_from):
                                info('balance of '+currency+' is too low on '+tx_hash)
                                # mark tx as invalid and continue
                                f=open('tx/'+tx_hash+'.json','r')
                                tmp_dict=json.load(f)[0]
                                f.close()
                                tmp_dict['invalid']=(True,'balance too low')
                                f=open('tx/'+tx_hash+'.json','w')
                                f.write('[')
                                json.dump(tmp_dict,f)
                                f.write(']\n')
                                f.close()
                            else:
                                # update to_addr
                                if not addr_dict.has_key(to_addr):
                                    if c==0:   #msc balance   #recieved  #sent                 #b #s #o #in #out #by #sld #offr #ex 
                                        addr_dict[to_addr]=([amount_transfer,amount_transfer,0,0, 0, 0, [t],[],  [], [],  [],   []],
                                                           #test balance #b #s #o #in #out #buy #sold #offer #ex
                                                           [0,0,0,       0, 0, 0, [], [],  [],  [],   [],    []],   [0])
                                    else:
                                        addr_dict[to_addr]=([0,0,0,0,0,0,[],[],[],[],[],[]],
                                                           [amount_transfer,amount_transfer,0,0,0,0,[t],[],[],[],[],[]],[0])
                                else:
                                    if c==0:
                                        addr_dict[to_addr][0][0]+=amount_transfer # msc
                                        addr_dict[to_addr][0][1]+=amount_transfer # msc total received
                                        addr_dict[to_addr][0][6].append(t)        # incoming msc
                                    else:                                    
                                        addr_dict[to_addr][1][0]+=amount_transfer # test msc
                                        addr_dict[to_addr][1][1]+=amount_transfer # test msc total received
                                        addr_dict[to_addr][1][6].append(t)        # incoming test msc
                                # update from_addr
                                if c==0:
                                    addr_dict[from_addr][0][0]-=amount_transfer # msc
                                    addr_dict[from_addr][0][2]+=amount_transfer # msc total sent
                                    addr_dict[from_addr][0][7].append(t)        # outgoing msc
                                    # update msc list
                                    sorted_mastercoin_tx_list.append(t) 
                                else:                                    
                                    addr_dict[from_addr][1][0]-=amount_transfer # test msc
                                    addr_dict[from_addr][1][2]+=amount_transfer # test msc total sent
                                    addr_dict[from_addr][1][7].append(t)        # outgoing test msc
                                    # update test msc list
                                    sorted_test_mastercoin_tx_list.append(t)

                    else:
                        # sell offer
                        if t['tx_type_str']==transaction_type_dict['00000014']:
                            debug(d, 'sell offer: '+tx_hash)
                            # sell offer from empty or non existing address is allowed
                            # update details of sell offer
                            # update single allowed tx for sell offer
                            # add to list to be shown on general
                            if c==0:
                                sorted_mastercoin_tx_list.append(t)
                            else:
                                sorted_test_mastercoin_tx_list.append(t)
                        else:
                            # sell accept
                            if t['tx_type_str']==transaction_type_dict['00000016']:
                                debug(d, 'sell accept: '+tx_hash)
                                # verify corresponding sell offer exists and partial balance
                                # partially fill and update balances and sell offer
                                # add to list to be shown on general
                                if c==0:
                                    sorted_mastercoin_tx_list.append(t)
                                else:
                                    sorted_test_mastercoin_tx_list.append(t)
                            else:
                                info('unknown tx type: '+t['tx_type_str']+' in '+tx_hash)
                                continue

        except OSError:
            info('error on tx '+t['tx_hash'])

    # create file for each address

    for addr in addr_dict.keys():
        addr_dict_api={}
        addr_dict_api['address']=addr
        for i in [0,1]:
            sub_dict={}
            sub_dict['received_transactions']=addr_dict[addr][i][6]
            sub_dict['received_transactions'].reverse()
            sub_dict['sent_transactions']=addr_dict[addr][i][7]
            sub_dict['sent_transactions'].reverse()
            sub_dict['total_received']=from_satoshi(addr_dict[addr][i][1])
            sub_dict['total_sent']=from_satoshi(addr_dict[addr][i][2])
            sub_dict['balance']=from_satoshi(addr_dict[addr][i][0])
            sub_dict['exodus_transactions']=addr_dict[addr][i][11]
            sub_dict['exodus_transactions'].reverse()
            sub_dict['total_exodus']=from_satoshi(addr_dict[addr][2][0])
            addr_dict_api[i]=sub_dict
        filename='addr/'+addr+'.json'
        f=open(filename, 'w')
        json.dump(addr_dict_api, f)
        f.close()

    # create files for msc and files for test_msc
    chunk=10
    sorted_mastercoin_tx_list.reverse()
    sorted_test_mastercoin_tx_list.reverse()

    for i in range(len(sorted_mastercoin_tx_list)/chunk):
    	filename='general/MSC_'+'{0:04}'.format(i)+'.json'
        f=open(filename, 'w')
        json.dump(sorted_mastercoin_tx_list[i*chunk:(i+1)*chunk], f)
        f.close()
    for i in range(len(sorted_test_mastercoin_tx_list)/chunk):
        filename='general/TMSC_'+'{0:04}'.format(i)+'.json'
        f=open(filename, 'w')
        json.dump(sorted_test_mastercoin_tx_list[i*chunk:(i+1)*chunk], f)
        f.close()

if __name__ == "__main__":
    main()
