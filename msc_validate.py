#!/usr/bin/python
import os
from optparse import OptionParser
from msc_utils_validating import *

# alarm to release funds if accept not paid on time
# format is {block:[accept_tx1, accept_tx2, ..], ..}
alarm={}

# create address dict that holds all details per address
addr_dict={}
tx_dict={}

# prepare lists for mastercoin and test
sorted_currency_tx_list={'Mastercoin':[],'Test Mastercoin':[]} # list 0 for mastercoins, list 1 for test mastercoins
sorted_currency_sell_tx_list={'Mastercoin':[],'Test Mastercoin':[]} # list 0 for mastercoins, list 1 for test mastercoins
sorted_currency_accept_tx_list={'Mastercoin':[],'Test Mastercoin':[]} # list 0 for mastercoins, list 1 for test mastercoins

# all available properties of a transaction
tx_properties=\
    ['tx_hash', 'invalid', 'tx_time', \
     'amount', 'formatted_amount', \
     'from_address', 'to_address', 'transactionType', \
     'icon', 'icon_text', 'color', \
     'block', 'index', \
     'details', 'tx_type_str', \
     'baseCoin', 'dataSequenceNum', 'method', 'tx_method_str', \
     'bitcoin_amount_desired', 'block_time_limit', 'fee', \
     'sell_offer_txid', 'accept_txid', 'btc_offer_txid', 'payment_txid', \
     'amount_available', 'formatted_amount_available', \
     'formatted_amount_accepted', 'formatted_amount_bought', \
     'formatted_amount_requested', 'formatted_price_per_coin', 'bitcoin_required', \
     'payment_done', 'payment_expired', \
     'status']

# all available properties of a currency in address
addr_properties=['balance', 'received', 'sent', 'bought', 'sold', 'offer', 'accept',\
            'in_tx', 'out_tx', 'bought_tx', 'sold_tx', 'offer_tx', 'accept_tx', 'exodus_tx']

# coins and their numbers
coins_list=['Mastercoin', 'Test Mastercoin']
coins_dict={'Mastercoin':'0','Test Mastercoin':'1'}
coins_short_name_dict={'Mastercoin':'MSC','Test Mastercoin':'TMSC'}
coins_reverse_short_name_dict=dict((v,k) for k, v in coins_short_name_dict.iteritems())

# create modified tx dict which would be used to modify tx files
bids_dict={}

# global last block on the net
last_height=get_last_height()

def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

def initial_tx_dict_load():
    # run on all files in tx
    tx_files=sorted_ls('tx')

    # load dict of each
    for filename in tx_files:
        if filename.endswith('.json'):
            tx_hash=filename.split('.')[0]
            update_tx_dict(tx_hash)

def get_sorted_tx_list():
    # run on all files in tx
    tx_files=sorted_ls('tx')

    # load dict of each
    tx_list=[]
    for k in tx_dict.keys():
        tx_list+=tx_dict[k] # append the list of tx for each key (incl. exodus)
    # sort according to time
    return sorted(tx_list, key=lambda k: (int(k['block']),int(k['index']))) 

def add_alarm(tx_hash, payment_timeframe):
    t=tx_dict[tx_hash][-1] # last tx on the list
    tx_block=int(t['block'])
    alarm_block=tx_block+payment_timeframe
    if alarm.has_key(alarm_block):
        alarm[alarm_block].append(t)
    else:
        alarm[alarm_block]=[t]

def check_alarm(t, last_block, current_block):
    # check alarms for all blocks since last check
    for b in range(last_block, current_block):
        if alarm.has_key(b):
            debug('alarm for block '+str(b))
            for a in alarm[b]:
                debug('verify payment for tx '+str(a['tx_hash']))
                # mark invalid and update standing accept value
                tx_hash=a['tx_hash']
                if not a.has_key('btc_offer_txid') or a['btc_offer_txid']=='unknown': # accept with no payment
                    debug('accept offer expired '+tx_hash)
                    update_tx_dict(tx_hash, payment_expired=True, color='bgc-expired', \
                        icon_text='Payment expired', formatted_amount_bought='0.0', status='Expired')
                else:
                    debug('accept offer done '+tx_hash)  
                    update_tx_dict(tx_hash, payment_done=True, color='bgc-done', \
                        icon_text='Payment done', status='Closed')

def check_bitcoin_payment(t):
    if t['invalid']==[True, 'bitcoin payment']:
        from_address=t['from_address']
        current_block=int(t['block'])
        # was there accept from this address to any of the payment addresses?
        to_multi_address_and_amount=t['to_address'].split(';')
        for address_and_amount in to_multi_address_and_amount:
            (address,amount)=address_and_amount.split(':')
            if address!=exodus_address:
                # check if it fits to a sell offer in address
                # first check if msc sell offer exists
                sell_offer_tx=None
                sell_accept_tx=None
                required_btc=0
                for c in coins_list: # check for offers of Mastercoin or Test Mastercoin
                    try:
                        sell_offer_tx=addr_dict[address][c]['offer_tx'][-1]
                        break
                    except (IndexError,KeyError):
                        pass
                # any relevant sell offer found?
                if sell_offer_tx != None:
                    debug('bitcoin payment: '+t['tx_hash'])
                    debug('for sell offer: '+sell_offer_tx['tx_hash'])

# stopped here
# I want to have tx only in tx_dict, and in addr_dict only tx_hash's
# Can introduce (sorted)json hash, hash of hashes, and this push to blockchain for suported parser versions.
# auto verify that parsing is correct

                    try:
                        required_btc=float(sell_offer_tx['formatted_bitcoin_amount_desired'])
                        whole_sell_amount=float(sell_offer_tx['formatted_amount'])
                        block_time_limit=int(sell_offer_tx['formatted_block_time_limit'])
                    except KeyError:
                        error('sell offer with missing details: '+sell_offer_tx['tx_hash'])
                    # now find the relevant accept and verify details (also partial purchase)
                    try:
                        sell_accept_tx_list=addr_dict[from_address][c]['accept_tx']
                    except KeyError:
                        debug('no accept_tx on '+from_address)
                        continue
                    for sell_accept_tx in sell_accept_tx_list: # go over all accepts
                        # now check if block time limit is as required
                        sell_accept_block=int(sell_accept_tx['block'])
                        # if sell accept is valid, then fee is OK - no need to re-check
                        if sell_accept_block+block_time_limit >= current_block:
                            part_bought=float(amount)/required_btc
                            if part_bought>0:
                                # mark deal as closed
                                # calculate the spot accept
                                try:
                                    spot_accept=float(sell_accept_tx['formatted_amount_accepted'])
                                except KeyError:
                                    debug('continue to next accept, since no formatted_amount_accepted on '+sell_accept_tx['tx_hash'])
                                    # this was not the right accept
                                    continue
                                spot_closed=min((part_bought*float(whole_sell_amount)+0.000000005), spot_accept)

                                # update sold tx
                                satoshi_spot_closed=to_satoshi(spot_closed)
                                update_addr_dict(address, True, c, balance=-satoshi_spot_closed, sold=satoshi_spot_closed, \
                                    offer=-satoshi_spot_closed, accept=-satoshi_spot_closed, sold_tx=sell_accept_tx)

                                # update bought tx
                                update_addr_dict(from_address, True, c, balance=satoshi_spot_closed, \
                                    bought=satoshi_spot_closed, bought_tx=sell_accept_tx)

                                # update sell available: min between original sell amount, the remaining offer, and the current balance
                                update_tx_dict(sell_offer_tx['tx_hash'], amount_available=min(float(sell_offer_tx['formatted_amount']), \
                                    from_satoshi(addr_dict[from_address][c]['offer']),from_satoshi(addr_dict[from_address][c]['balance'])))
                                update_tx_dict(sell_offer_tx['tx_hash'], formatted_amount_available=formatted_decimal(sell_offer_tx['amount_available']))

                                # if not more left in the offer - close sell
                                if addr_dict[address][c]['offer'] == 0:
                                    update_tx_dict(sell_accept_tx['tx_hash'], color='bgc-done', icon_text='Sell offer done')
                                else:
                                    update_tx_dict(sell_accept_tx['tx_hash'], color='bgc-accepted-done', icon_text='Sell offer partially done')

                                # update sell accept tx (with bitcoin payment etc)
                                update_tx_dict(sell_accept_tx['tx_hash'], btc_offer_txid=t['tx_hash'], status='Closed', \
                                    payment_done=True, formatted_amount_bought=from_satoshi(satoshi_spot_closed),  \
                                    color='bgc-done', icon_text='Accept offer paid')

                                # update sell and accept offer in bitcoin payment
                                update_tx_dict(t['tx_hash'], sell_offer_txid=sell_offer_tx['tx_hash'], accept_txid=sell_accept_tx['tx_hash'])

                                # update the sorted currency tx list
                                return True # hidden assumption: payment is for a single accept
                            else:
                                error('non positive part bought on bitcoin payment: '+t['tx_hash'])
                        else:
                            debug('payment does not fit to accept: '+sell_accept_tx['tx_hash'])
    return False


# A fresh initialized address entry
def new_addr_entry():
    entry={}
    # for each currency
    for c in coins_list+['Bitcoin']:
        currency_dict={}
        # initialize all properties
        for property in addr_properties:
            if property.endswith('_tx'):
                 currency_dict[property]=[]
            else:
                 currency_dict[property]=0
        entry[c]=currency_dict
    entry['exodus']={'bought':0}
    return entry


# update the main tx database
# example call:
# update_tx_dict(tx_hash, icon='simplesend', color='bgc_done')
def update_tx_dict(tx_hash, *arguments, **keywords):
    # tx_hash is first arg
    # then come the keywords and values to be modified

    # is there already entry for this tx_hash?
    if not tx_dict.has_key(tx_hash):
        # no - so create a new one
        # remark: loading all tx for that tx_hash
        # for simplesend which is exodus, the last one is simplesend (#1)
        tx_dict[tx_hash]=load_dict_from_file('tx/'+tx_hash+'.json', all_list=True)

    # the last tx on the list is the one to modify
    n=-1

    # get the update_fs from tx_dict for that tx
    if tx_dict[tx_hash][n].has_key('update_fs'):
        update_fs=tx_dict[tx_hash][n]['update_fs']
    else:
        # start with default "no need to update fs"
        tx_dict[tx_hash][n]['update_fs']=False
        update_fs=False
    
    # update all given fields with new values
    keys = sorted(keywords.keys())
    # allow only keys from tx_properties
    for kw in keys:
        try:
            prop_index=tx_properties.index(kw)
        except ValueError:
            error('unsupported property of tx: '+kw)
        # set update_fs flag if necessary (if something really changed)
        try:
            update_fs = tx_dict[tx_hash][n][kw]!=keywords[kw] or update_fs
        except KeyError:
            update_fs = True
        tx_dict[tx_hash][n][kw]=keywords[kw]

    tx_dict[tx_hash][n]['update_fs']=update_fs


# update the main address database
# example call:
# update_addr_dict('1address', True, 'Mastercoin', balance=10, bought=2, bought_tx=t)
# accomulate True means add on top of previous values
# accomulate False means replace previous values
def update_addr_dict(addr, accomulate, *arguments, **keywords):

    # update specific currency fields within address
    # address is first arg
    # currency is second arg:
    # 'Mastercoin', 'Test Mastercoin', 'Bitcoin' or 'exodus' for exodus purchases
    # then come the keywords and values to be updated
    c=arguments[0]
    if c!='Mastercoin' and c!='Test Mastercoin' and c!='exodus' and c!= 'Bitcoin':
        error('update_addr_dict called with unsupported currency: '+c)

    # is there already entry for this address?
    if not addr_dict.has_key(addr):
        # no - so create a new one
        addr_dict[addr]=new_addr_entry()

    # update all given fields with new values
    keys = sorted(keywords.keys())
    # allow only keys from addr_properties
    for kw in keys:
        try:
            prop_index=addr_properties.index(kw)
        except ValueError:
            error('unsupported property of addr: '+kw)

        if accomulate == True: # just add the tx or value
            if kw.endswith('_tx'):
                addr_dict[addr][c][kw].append(keywords[kw])
            else: # values are in satoshi
                addr_dict[addr][c][kw]+=int(keywords[kw])
        else:
            if kw.endswith('_tx'): # replace the tx or value
                addr_dict[addr][c][kw]=[keywords[kw]]
            else: # values are in satoshi
                addr_dict[addr][c][kw]=int(keywords[kw])


def update_initial_icon_details(t):
    # update fields icon, details
    update_tx_dict(t['tx_hash'], color='bgc-new')
    try:
        if t['transactionType']=='00000000':
            update_tx_dict(t['tx_hash'], icon='simplesend', details=t['to_address'])
        else:
            if t['transactionType']=='00000014':
                update_tx_dict(t['tx_hash'], icon='selloffer', details=t['formatted_price_per_coin'])
            else:
                if t['transactionType']=='00000016':
                    update_tx_dict(t['tx_hash'], icon='sellaccept', details='unknown_price')
                else:
                    update_tx_dict(t['tx_hash'], icon='unknown', details='unknown')
    except KeyError as e:
        # The only *valid* mastercoin tx without transactionType is exodus
        if t['tx_type_str']=='exodus':
            try:
                update_tx_dict(t['tx_hash'], icon='exodus', details=t['to_address'])
            except KeyError:
                error('exodus tx with no to_address: '+str(t))
        else:
            error('non exodus valid msc tx without '+e+' ('+t['tx_type_str']+') on '+tx_hash)

def mark_tx_invalid(tx_hash, reason):
    # mark tx as invalid
    update_tx_dict(tx_hash, invalid=(True,reason), color='bgc-invalid')

# add another sell tx to the modified dict
def add_bids(key, t):
    if bids_dict.has_key(key):
        bids_dict[key].append(t)
    else:
        bids_dict[key]=[t]


# write back to fs all tx which got modified
def write_back_modified_tx():
    n=-1 # relevant is last tx on the list
    for k in tx_dict.keys():
        if tx_dict[k][n]['update_fs'] == True:
            # remove update fs marker
            del tx_dict[k][n]['update_fs']
            # save back to filesystem
            atomic_json_dump(tx_dict[k], 'tx/'+k+'.json', add_brackets=False)

# create bids json
def update_bids():
    for tx_hash in bids_dict.keys():
        # write updated bids
        atomic_json_dump(bids_dict[tx_hash], 'bids/bids-'+tx_hash+'.json', add_brackets=False)

def update_bitcoin_balances():
    chunk=100
    addresses=addr_dict.keys()

    # cut into chunks
    for i in range(len(addresses)/chunk):
        addr_batch=addresses[i*chunk:(i+1)*chunk]

        # create the string of all addresses
        addr_batch_str=''
        for a in addr_batch:
            addr_batch_str=addr_batch_str+a+' '

        # get the balances
        balances=get_balance(addr_batch_str)

        # update addr_dict with bitcoin balance
        for b in balances:
            update_addr_dict(b['address'], False, 'Bitcoin', balance=b['paid'])
       
 
# generate api json
# address
# general files (10 in a page)
# mastercoin_verify
def generate_api_jsons():

    # prepare updated snapshot of bitcoin balances for all addresses
    update_bitcoin_balances()

    # create file for each address
    for addr in addr_dict.keys():
        balances_list=[]
        addr_dict_api={}
        addr_dict_api['address']=addr
        for c in coins_list:
            sub_dict={}
            sub_dict['received_transactions']=addr_dict[addr][c]['in_tx']
            sub_dict['received_transactions'].reverse()
            sub_dict['sent_transactions']=addr_dict[addr][c]['out_tx']
            sub_dict['sent_transactions'].reverse()
            sub_dict['bought_transactions']=addr_dict[addr][c]['bought_tx']
            sub_dict['bought_transactions'].reverse()
            sub_dict['sold_transactions']=addr_dict[addr][c]['sold_tx']
            sub_dict['sold_transactions'].reverse()
            sub_dict['offer_transactions']=addr_dict[addr][c]['offer_tx']
            sub_dict['offer_transactions'].reverse()
            sub_dict['accept_transactions']=addr_dict[addr][c]['accept_tx']
            sub_dict['accept_transactions'].reverse()
            sub_dict['total_received']=from_satoshi(addr_dict[addr][c]['received'])
            sub_dict['total_sent']=from_satoshi(addr_dict[addr][c]['sent'])
            sub_dict['total_sold']=from_satoshi(addr_dict[addr][c]['sold'])
            sub_dict['total_bought']=from_satoshi(addr_dict[addr][c]['bought'])
            sub_dict['total_sell_accept']=from_satoshi(addr_dict[addr][c]['accept'])
            sub_dict['total_sell_offer']=from_satoshi(addr_dict[addr][c]['offer'])
            sub_dict['balance']=from_satoshi(addr_dict[addr][c]['balance'])
            sub_dict['exodus_transactions']=addr_dict[addr][c]['exodus_tx']
            sub_dict['exodus_transactions'].reverse()
            sub_dict['total_exodus']=from_satoshi(addr_dict[addr]['exodus']['bought'])
            balances_list.append({"symbol":coins_short_name_dict[c],"value":sub_dict['balance']})
            addr_dict_api[coins_dict[c]]=sub_dict
        balances_list.append({"symbol":"BTC","value":from_satoshi(addr_dict[addr]['Bitcoin']['balance'])})
        addr_dict_api['balance']=balances_list
        atomic_json_dump(addr_dict_api, 'addr/'+addr+'.json', add_brackets=False)

    # create files for msc and files for test_msc
    for k in tx_dict.keys():
        # take all tx list for this txid
        for t in tx_dict[k]:
            if t['invalid'] != False:
                continue
            if t['tx_type_str']=='exodus':
                sorted_currency_tx_list['Mastercoin'].append(t)
                sorted_currency_tx_list['Test Mastercoin'].append(t)
            else:
                if t['currencyId']==reverse_currency_type_dict['Mastercoin']:
                    sorted_currency_tx_list['Mastercoin'].append(t)
                else:
                    if t['currencyId']==reverse_currency_type_dict['Test Mastercoin']:
                        sorted_currency_tx_list['Test Mastercoin'].append(t)
    # and reverse sort
    for c in coins_list:
        sorted_currency_tx_list[c]=sorted(sorted_currency_tx_list[c], \
            key=lambda k: (-int(k['block']),-int(k['index'])))

    chunk=10
    # create the latest transactions pages
    pages={'Mastercoin':0, 'Test Mastercoin':0}
    for c in coins_list:
        for i in range(len(sorted_currency_tx_list[c])/chunk):
            atomic_json_dump(sorted_currency_tx_list[c][i*chunk:(i+1)*chunk], \
                'general/'+coins_short_name_dict[c]+'_'+'{0:04}'.format(i+1)+'.json', add_brackets=False)
            pages[c]+=1

    # create the latest accept transactions page
    for c in coins_list:
        for t in sorted_currency_tx_list[c]:
            if t['tx_type_str']=='Sell accept':
                sorted_currency_accept_tx_list[c].append(t)

    accept_pages={'Mastercoin':0, 'Test Mastercoin':0}
    for c in coins_list:
        for i in range(len(sorted_currency_accept_tx_list[c])/chunk):
            atomic_json_dump(sorted_currency_accept_tx_list[c][i*chunk:(i+1)*chunk], \
                'general/'+coins_short_name_dict[c]+'_accept_'+'{0:04}'.format(i+1)+'.json', add_brackets=False)
            accept_pages[c]+=1

    # update values.json
    values_list=load_dict_from_file('www/values.json', all_list=True, skip_error=True)
    # on missing values.json, take an empty default
    if values_list=={}:
        values_list=[{"currency": "MSC", "name": "Mastercoin", "name2": "", "pages": 1, "trend": "down", "trend2": "rgb(13,157,51)"}, \
                     {"currency": "TMSC", "name": "Test MSC", "name2": "", "pages": 1, "trend": "up", "trend2": "rgb(212,48,48)"}]
    updated_values_list=[]
    for v in values_list:
        v['pages']=pages[coins_reverse_short_name_dict[v['currency']]]
        v['accept_pages']=accept_pages[coins_reverse_short_name_dict[v['currency']]]
        updated_values_list.append(v)
    atomic_json_dump(updated_values_list, 'www/values.json', add_brackets=False)

    # create /mastercoin_verify/addresses/$currency
    for c in coins_list:
        mastercoin_verify_list=[]
        subdir=coins_dict[c]
        for addr in addr_dict.keys():
            sub_dict={}
            sub_dict['address']=addr
            sub_dict['balance']=from_satoshi(addr_dict[addr][c]['balance'])
            mastercoin_verify_list.append(sub_dict)
        atomic_json_dump(sorted(mastercoin_verify_list, key=lambda k: k['address']), 'mastercoin_verify/addresses/'+subdir, add_brackets=False)

    # create /mastercoin_verify/transactions/<ADDRESS>
    for addr in addr_dict.keys():
        single_addr_tx_dict={}
        verify_tx_dict={}
        verify_tx_list=[]
        for c in coins_list:
            for t in addr_dict[addr][c]['exodus_tx']+addr_dict[addr][c]['in_tx']+addr_dict[addr][c]['out_tx']:
                if t['invalid']==False:
                    verify_tx_dict[t['tx_hash']]=True
                else:
                    verify_tx_dict[t['tx_hash']]=False
        # collect all unique entries
        for key, value in verify_tx_dict.iteritems():
            verify_tx_list.append({'tx_hash':key, 'valid':value})
        mastercoin_verify_tx_per_address={'address':addr, 'transactions':verify_tx_list}
        atomic_json_dump(mastercoin_verify_tx_per_address, 'mastercoin_verify/transactions/'+addr, add_brackets=False)     
        

# validate a matercoin transaction
def check_mastercoin_transaction(t, index=-1):

    # update icon and details
    update_initial_icon_details(t)
    t=tx_dict[t['tx_hash']][index]

    # get general data from tx
    to_addr=t['to_address']
    from_addr=t['from_address']
    amount_transfer=to_satoshi(t['formatted_amount'])
    currency=t['currency_str']
    tx_hash=t['tx_hash']
    tx_age=int(last_height) - int(t['block'])+1
    try:
        is_exodus=t['exodus']
    except KeyError:
        is_exodus=False

    if is_exodus: # assume exodus does not do sell offer/accept
        # exodus purchase
        update_addr_dict(to_addr, True, 'Mastercoin', balance=amount_transfer, exodus_tx=t)
        update_addr_dict(to_addr, True, 'Test Mastercoin', balance=amount_transfer, exodus_tx=t)
        update_addr_dict(to_addr, True, 'exodus', bought=amount_transfer)
        # exodus bonus - 10% for exodus (available slowly during the years)
        ten_percent=int((amount_transfer+0.0)/10+0.5)
        update_addr_dict(exodus_address, True, 'Mastercoin', balance=ten_percent, exodus_tx=t)
        update_addr_dict(exodus_address, True, 'Test Mastercoin', balance=ten_percent, exodus_tx=t)

        # all exodus are done
        update_tx_dict(t['tx_hash'], color='bgc-done', icon_text='Exodus')
    else:
        c=currency
        if c!='Mastercoin' and c!='Test Mastercoin':
            debug('unknown currency '+currency+ ' in tx '+tx_hash)
            return False
        # left are normal transfer and sell offer/accept
        if t['tx_type_str']==transaction_type_dict['00000000']:
            if tx_age <= blocks_consider_new:
                update_tx_dict(t['tx_hash'], color='bgc-new', icon_text='Simple send ('+str(tx_age)+' confirms)')
            else:
                if tx_age < blocks_consider_mature:
                    update_tx_dict(t['tx_hash'], color='bgc-new-done', icon_text='Simple send ('+str(tx_age)+' confirms)')
                else:
                    update_tx_dict(t['tx_hash'], color='bgc-done', icon_text='Simple send')
 
            # the normal transfer case
            if not addr_dict.has_key(from_addr):
                debug('try to pay from non existing address at '+tx_hash)
                mark_tx_invalid(tx_hash, 'pay from a non existing address')
                return False 
            else:
                balance_from=addr_dict[from_addr][c]['balance']
                if amount_transfer > int(balance_from):
                    debug('balance of '+currency+' is too low on '+tx_hash)
                    mark_tx_invalid(tx_hash, 'balance too low')
                    return False
                else:
                    # update to_addr
                    update_addr_dict(to_addr, True, c, balance=amount_transfer, received=amount_transfer, in_tx=t)
                    # update from_addr
                    update_addr_dict(from_addr, True, c, balance=-amount_transfer, sent=amount_transfer, out_tx=t)
                    return True
        else:
            # sell offer
            if t['tx_type_str']==transaction_type_dict['00000014']:
                debug('sell offer: '+tx_hash)
                # update sell available: min between original sell amount and the current balance
                try:
                    seller_balance=from_satoshi(addr_dict[from_addr][c]['balance'])
                except KeyError: # no such address
                    seller_balance=0.0
                amount_available=min(float(t['formatted_amount']), seller_balance)
                update_tx_dict(t['tx_hash'], icon_text='Sell Offer ('+str(tx_age)+' confirms)', \
                    amount_available=amount_available, formatted_amount_available=formatted_decimal(amount_available))
                # sell offer from empty or non existing address is allowed
                # update details of sell offer
                # update single allowed tx for sell offer
                # add to list to be shown on general
                offer_amount=to_satoshi(t['formatted_amount'])
                update_addr_dict(from_addr, True, c, offer=offer_amount, offer_tx=t)
                return True
            else:
                # sell accept
                if t['tx_type_str']==transaction_type_dict['00000016']:
                    debug('sell accept: '+tx_hash)

                    update_tx_dict(t['tx_hash'], icon_text='Sell Accept (active)')
                    # verify corresponding sell offer exists and partial balance
                    # partially fill and update balances and sell offer
                    # add to list to be shown on general
                    # partially fill according to spot offer  

                    try:
                        accept_amount_requested=t['formatted_amount_requested']
                    except KeyError:
                        accept_amount_requested=0.0
                    try:
                        sell_offer=addr_dict[to_addr][c]['offer']           # get orig offer from seller
                        sell_offer_tx=addr_dict[to_addr][c]['offer_tx'][-1] # get orig offer tx (last) from seller
                    except (KeyError, IndexError):
                        # offer from wallet without entry (empty wallet)
                        info('accept offer from missing seller '+to_addr)
                        mark_tx_invalid(tx_hash, 'accept offer of missing sell offer')
                        return False

                    # required fee calculation
                    try:
                        required_fee=float(sell_offer_tx['formatted_required_fee'])
                    except KeyError:
                        required_fee=0.0
                    try:
                        accept_fee=float(t['formatted_fee'])
                    except KeyError:
                        accept_fee=0.0
                    if accept_fee<required_fee:
                        info('accept offer without minimal fee on tx: '+tx_hash)
                        mark_tx_invalid(tx_hash, 'accept offer without required fee')
                        return False

                    try:
                        formatted_price_per_coin=sell_offer_tx['formatted_price_per_coin']
                    except KeyError:
                        formatted_price_per_coin='price missing'
                    t['formatted_price_per_coin']=formatted_price_per_coin
                    try:
                        # need to pay the part of the sell offer which got accepted
                        part=float(t['formatted_amount_accepted'])/float(sell_offer_tx['formatted_amount'])
                        bitcoin_required=float(sell_offer_tx['formatted_bitcoin_amount_desired'])*part
                    except KeyError:
                        bitcoin_required='missing required btc'

                    update_tx_dict(t['tx_hash'], bitcoin_required=bitcoin_required, sell_offer_txid=sell_offer_tx['tx_hash'], \
                        btc_offer_txid='unknown')

                    spot_accept=min(float(sell_offer),float(accept_amount_requested))   # the accept is on min of all
                    if spot_accept > 0: # ignore 0 or negative accepts

                        update_tx_dict(t['tx_hash'], formatted_amount_accepted=spot_accept, payment_done=False, payment_expired=False)
                        payment_timeframe=int(sell_offer_tx['formatted_block_time_limit'])
                        add_alarm(t['tx_hash'], payment_timeframe)

                        # accomulate the spot accept on the seller side
                        update_addr_dict(from_addr, True, c, accept=to_satoshi(spot_accept), accept_tx=t)

                        # update icon colors of sell
                        if sell_offer > spot_accept:
                            update_tx_dict(sell_offer_tx['tx_hash'], color='bgc-new-accepted', icon_text='Sell offer partially accepted')
                        else:
                            update_tx_dict(sell_offer_tx['tx_hash'], color='bgc-accepted', icon_text='Sell offer accepted')
                    else:
                        mark_tx_invalid(t['tx_hash'],'non positive spot accept')
                    # add to current bids (which appear on seller tx)
                    key=sell_offer_tx['tx_hash']
                    add_bids(key, t)
                    return True
                else:
                    info('unknown tx type: '+t['tx_type_str']+' in '+tx_hash)
                    return False


#########################################################################
# main function - validates all tx and calculates balances of addresses #
#########################################################################
def validate():

    # parse command line arguments
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")

    (options, args) = parser.parse_args()
    msc_globals.init()
    msc_globals.d=options.debug_mode

    # don't bother validating if no new block was generated
    last_validated_block=0
    try:
        f=open(LAST_VALIDATED_BLOCK_NUMBER_FILE,'r')
        last_validated_block=int(f.readline())
        f.close()
        if last_validated_block == int(last_height):
            info('last validated block '+str(last_validated_block)+' is identical to current height')
            exit(0)
    except IOError:
        pass

    info('starting validation process')

    # load tx_dict
    initial_tx_dict_load()

    # get all tx sorted
    sorted_tx_list=get_sorted_tx_list()

    # keep the last block which will get validated
    updated_last_validated_block=sorted_tx_list[-1]['block']

    # use an artificial empty last tx with last height as a trigger for alarm check
    sorted_tx_list.append({'invalid':(True,'fake tx'), 'block':last_height, 'tx_hash':'fake'})

    last_block=0 # keep tracking of last block for alarm purposes

    # go over all tx
    for t in sorted_tx_list:

        # check alarm (verify accept offers get payment in time)
        try:
            current_block=int(t['block'])
        except ValueError:
            error('invalid block number during validation: '+t['block'])
        check_alarm(t, last_block, current_block)
        # update last_block for next alarm check
        last_block=current_block

        try:
            if t['invalid'] == False: # normal valid mastercoin tx
                try:
                    if t['exodus']==True:
                        index=0 # for exodus take the first tx on the list
                except KeyError:
                    index=-1 # otherwise take the last tx in the list
                check_mastercoin_transaction(t, index)
            else: # maybe bitcoin payment
                if check_bitcoin_payment(t):
                    continue
                else: # report reason for invalid tx
                   debug(str(t['invalid'])+' '+t['tx_hash'])

        except OSError:
            error('error on tx '+t['tx_hash'])

    # create json for bids
    update_bids()

    # update changed tx
    write_back_modified_tx()

    # generate address pages and last tx pages
    generate_api_jsons()

    # write last validated block
    f=open(LAST_VALIDATED_BLOCK_NUMBER_FILE,'w')
    f.write(str(last_block)+'\n')
    f.close()

    info('validation done')

if __name__ == "__main__":
    validate()
