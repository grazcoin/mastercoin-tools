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

# alarm to release funds if not paid
# format is {block:[accept_tx1, accept_tx2, ..], ..}
alarm={}

def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

def add_alarm(t, payment_timeframe):
    tx_block=int(t['block'])
    alarm_block=tx_block+payment_timeframe
    if alarm.has_key(alarm_block):
        alarm[alarm_block].append(t)
    else:
        alarm[alarm_block]=[t]

def get_sorted_tx_list():
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
    return sorted(tx_list, key=lambda k: (k['block'],k['index'])) 

def main():
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")

    (options, args) = parser.parse_args()
    d=options.debug_mode

    # get all tx sorted
    sorted_tx_list=get_sorted_tx_list()

    # use an artificial empty last tx with last height as a trigger for alarm check
    info('before')
    last_height=get_last_height()
    info(last_height)
    sorted_tx_list.append({'invalid':(True,'fake tx'), 'block':last_height, 'tx_hash':'fake'})

    # prepare lists for mastercoin and test
    sorted_currency_tx_list=[[],[]] # first list if for mastercoins, second for test mastercoins

    last_block=0 # keep tracking of last block for alarm purposes

    # create address dict and update balance of valid tx
    addr_dict={}
    # create modified tx dict and update changes
    modified_tx_dict={}
    for t in sorted_tx_list:

        # check alarm
        current_block=int(t['block'])
        for b in range(last_block,current_block):
            if alarm.has_key(b):
                debug(d, 'alarm for block '+str(b))
                for a in alarm[b]:
                    debug(d, 'verify payment for tx '+str(a))
                    # mark invalid and update standing accept value
        last_block=current_block

        try:
            if t['invalid']==[True, 'bitcoin payment']:
                debug(d, 'bitcoin payment: '+tx_hash)
                fee=t['fee']
                # check if it fits to any of the
                # mark deal as closed
                
                                #addr_dict[to_addr][c][5]-=spot_accept      # reduce balance of seller (conditionally)
                                #addr_dict[to_addr][c][5]-=spot_accept      # increase balance of buyer
                                #addr_dict[to_addr][c][5]-=spot_accept      # reduce offer of seller
                                #addr_dict[from_addr][c][5]-=spot_accept
                continue

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
                                             #msc balance    #received   #sent   #b #s #o #a #in  #out #buy #sold #offer #exodus
                        addr_dict[to_addr]=([amount_transfer,0,          0,      0, 0, 0, 0, [],  [],  [],  [],   [],    [t]],
                                #test msc balance #received  #sent   #b #s #o #a #in  #out #buy #sold #offer #exodus # exodus purchase
				[amount_transfer, 0,         0,      0, 0, 0, 0, [],  [],  [],  [],   [],    [t]],   [amount_transfer])
                    else:
                        addr_dict[to_addr][0][0]+=amount_transfer # msc
                        addr_dict[to_addr][1][0]+=amount_transfer # test msc
                        addr_dict[to_addr][0][12].append(t)       # incoming msc
                        addr_dict[to_addr][1][12].append(t)       # incoming test msc
                        addr_dict[to_addr][2][0]+=amount_transfer # exodus purchase
                    # exodus bonus - 10% for exodus (available slowly during the years)
                    ten_percent=int((amount_transfer+0.0)/10+0.5)
                    if not addr_dict.has_key(exodus_address):
                        addr_dict[exodus_address]=([ten_percent,0,0,0,0,0,0,[],[],[],[],[],[t]],[ten_percent,0,0,0,0,0,0,[],[],[],[],[],[t]],[0])
                    else:
                        addr_dict[exodus_address][0][0]+=ten_percent # 10% bonus msc for exodus
                        addr_dict[exodus_address][1][0]+=ten_percent # 10% bonus test msc for exodus
                        addr_dict[exodus_address][0][12].append(t)   # incoming msc
                        addr_dict[exodus_address][1][12].append(t)   # incoming test msc
                        addr_dict[exodus_address][2][0]+=0           # no accounting for exodus 10% due to purchase
                    # tx belongs to mastercoin and test mastercoin
                    sorted_currency_tx_list[0].append(t) 
                    sorted_currency_tx_list[1].append(t) 
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
                                    if c==0:   #msc balance   #recieved  #sent                 #b #s #o #a #in #out #by #sld #offr #ex 
                                        addr_dict[to_addr]=([amount_transfer,amount_transfer,0,0, 0, 0, 0, [t],[],  [], [],  [],   []],
                                                           #test balance #b #s #o #a #in #out #buy #sold #offer #ex
                                                           [0,0,0,       0, 0, 0, 0, [], [],  [],  [],   [],    []],   [0])
                                    else:
                                        addr_dict[to_addr]=([0,0,0,0,0,0,0,[],[],[],[],[],[]],
                                                           [amount_transfer,amount_transfer,0,0,0,0,0,[t],[],[],[],[],[]],[0])
                                else:
                                    addr_dict[to_addr][c][0]+=amount_transfer # msc
                                    addr_dict[to_addr][c][1]+=amount_transfer # msc total received
                                    addr_dict[to_addr][c][7].append(t)        # incoming msc
                                # update from_addr
                                addr_dict[from_addr][c][0]-=amount_transfer # msc
                                addr_dict[from_addr][c][2]+=amount_transfer # msc total sent
                                addr_dict[from_addr][c][8].append(t)        # outgoing msc
                                # update msc list
                                sorted_currency_tx_list[c].append(t) 

                    else:
                        # sell offer
                        if t['tx_type_str']==transaction_type_dict['00000014']:
                            debug(d, 'sell offer: '+tx_hash)
                            # sell offer from empty or non existing address is allowed
                            # update details of sell offer
                            # update single allowed tx for sell offer
                            # add to list to be shown on general
			    info(t)
                            offer=float(t['formatted_amount'])
                            addr_dict[from_addr][c][5]=offer      # update latest wish offer
                            addr_dict[from_addr][c][11]=[t]       # store the latest offer tx for ref
                            sorted_currency_tx_list[c].append(t)  # add per currency tx
                        else:
                            # sell accept
                            if t['tx_type_str']==transaction_type_dict['00000016']:
                                debug(d, 'sell accept: '+tx_hash)
                                # verify corresponding sell offer exists and partial balance
                                # partially fill and update balances and sell offer
                                # add to list to be shown on general
                                # partially fill according to spot offer
				info(t)
                                accept=float(t['formatted_amount'])
                                info(to_addr)
                                try:
                                    offer=addr_dict[to_addr][c][5]              # get orig offer from seller
                                    offer_tx=addr_dict[to_addr][c][11][0]       # get orig offer tx from seller
                                except (KeyError, IndexError):
                                    # offer from wallet without entry (empty wallet)
                                    # FIXME: mark tx invalid
                                    info('accept offer from empty seller - ignoring')
                                    continue
                                try:
                                    available=addr_dict[from_addr][c][0]    # get balance of that currency of buyer
                                except (KeyError, IndexError):
                                    info('accept offer to empty buyer balance - ignoring')
                                    continue
                                spot_offer=min(offer,available)             # limited by available balance of seller
                                spot_accept=min(spot_offer,accept)          # deal is limited by amount accepted by buyer
                                if spot_accept > 0: # ignore 0 or negative accepts
                                    t['spot_accept']=spot_accept
                                    t['payment_done']=False
                                    t['payment_expired']=False
                                    payment_timeframe=int(offer_tx['formatted_block_time_limit'])
                                    add_alarm(t,payment_timeframe)
                                    addr_dict[to_addr][c][6]+=spot_accept   # update accept
                                    addr_dict[to_addr][c][10].append(t)     # update bids on the offer
                                    sorted_currency_tx_list[c].append(t)    # add per currency tx
                                    # add to current bids (which appear on seller tx)
                                    key=offer_tx['tx_hash']
                                    if modified_tx_dict.has_key(key):
                                        modified_tx_dict[key].append(t)
                                    else:
                                        modified_tx_dict[key]=[t]
                                else:
                                    info('non positive spot accept')
                                    continue
                            else:
                                info('unknown tx type: '+t['tx_type_str']+' in '+tx_hash)
                                continue

        except OSError:
            info('error on tx '+t['tx_hash'])

    # update sell/accept tx files (FIXME: make sure modifications include alarms)
    for tx_hash in modified_tx_dict.keys():
        # open tx file
        f=open('tx/'+tx_hash+'.json','r')
        tmp_dict=json.load(f)[0]
        f.close()
        updated_tx=[tmp_dict]
        for t in modified_tx_dict[tx_hash]:
            updated_tx.append(t)
        f=open('tx/'+tx_hash+'.json','w')
        json.dump(updated_tx, f) 
        f.close()
        # add additional tx
        # close file 

    # create file for each address
    for addr in addr_dict.keys():
        addr_dict_api={}
        addr_dict_api['address']=addr
        for i in [0,1]:
            sub_dict={}
            sub_dict['received_transactions']=addr_dict[addr][i][7]
            sub_dict['received_transactions'].reverse()
            sub_dict['sent_transactions']=addr_dict[addr][i][8]
            sub_dict['sent_transactions'].reverse()
            sub_dict['total_received']=from_satoshi(addr_dict[addr][i][1])
            sub_dict['total_sent']=from_satoshi(addr_dict[addr][i][2])
            sub_dict['balance']=from_satoshi(addr_dict[addr][i][0])
            sub_dict['exodus_transactions']=addr_dict[addr][i][12]
            sub_dict['exodus_transactions'].reverse()
            sub_dict['total_exodus']=from_satoshi(addr_dict[addr][2][0])
            addr_dict_api[i]=sub_dict
        filename='addr/'+addr+'.json'
        f=open(filename, 'w')
        json.dump(addr_dict_api, f)
        f.close()

    # create files for msc and files for test_msc
    chunk=10
    sorted_currency_tx_list[0].reverse()
    sorted_currency_tx_list[1].reverse()

    for i in range(len(sorted_currency_tx_list[0])/chunk):
    	filename='general/MSC_'+'{0:04}'.format(i)+'.json'
        f=open(filename, 'w')
        json.dump(sorted_currency_tx_list[0][i*chunk:(i+1)*chunk], f)
        f.close()
    for i in range(len(sorted_currency_tx_list[1])/chunk):
        filename='general/TMSC_'+'{0:04}'.format(i)+'.json'
        f=open(filename, 'w')
        json.dump(sorted_currency_tx_list[1][i*chunk:(i+1)*chunk], f)
        f.close()

if __name__ == "__main__":
    main()
