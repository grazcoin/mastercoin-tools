#!/usr/bin/python
import os
from optparse import OptionParser
from msc_utils_validating import *

# alarm to release funds if accept not paid on time
# format is {block:[accept_tx1, accept_tx2, ..], ..}
alarm={}

# create address dict that holds all details per address
addr_dict={}

# prepare lists for mastercoin and test
sorted_currency_tx_list={'Mastercoin':[],'Test Mastercoin':[]} # list 0 for mastercoins, list 1 for test mastercoins

# all available properties of a currency in address
addr_properties=['balance', 'received', 'sent', 'bought', 'sold', 'offer', 'accept',\
            'in_tx', 'out_tx', 'bought_tx', 'sold_tx', 'offer_tx', 'accept_tx', 'exodus_tx']

# coins and their numbers
coins_list=['Mastercoin', 'Test Mastercoin']
coins_dict={'Mastercoin':'0','Test Mastercoin':'1'}
coins_short_name_dict={'Mastercoin':'MSC','Test Mastercoin':'TMSC'}
coins_reverse_short_name_dict=dict((v,k) for k, v in coins_short_name_dict.iteritems())

# create modified tx dict which would be used to modify tx files
modified_tx_dict={}

def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

def get_sorted_tx_list():
    # run on all files in tx
    tx_files=sorted_ls('tx')

    # load dict of each
    tx_list=[]
    for filename in tx_files:
        if filename.endswith('.json'):
            f=open('tx/'+filename)
            t_list=json.load(f)
            try:
                t=t_list[0] # normally take only first tx from list
            except (KeyError, IndexError):
                info('failed getting first tx from '+filename)
            tx_list.append(t)
            try: # for exodus
                if t['tx_type_str'] == 'exodus':
                    tx_list.append(t_list[1])
            except:
                pass
            f.close()
    # sort according to time
    return sorted(tx_list, key=lambda k: (k['block'],k['index'])) 

def add_alarm(t, payment_timeframe):
    tx_block=int(t['block'])
    alarm_block=tx_block+payment_timeframe
    if alarm.has_key(alarm_block):
        alarm[alarm_block].append(t)
    else:
        alarm[alarm_block]=[t]

def check_alarm(t, last_block, current_block):
    for b in range(last_block, current_block):
        if alarm.has_key(b):
            debug('alarm for block '+str(b))
            for a in alarm[b]:
                debug('verify payment for tx '+str(a))
                # mark invalid and update standing accept value

def check_bitcoin_payment(t):
    if t['invalid']==[True, 'bitcoin payment']:
        fee=t['fee']
        from_address=t['from_address']
        current_block=t['block']
        # was there accept from this address to any of the payment addresses?
        to_multi_address_and_amount=t['to_address'].split(';')
        for address_and_amount in to_multi_address_and_amount:
            (address,amount)=address_and_amount.split(':')
            if address!=exodus_address:
                # check if it fits to a sell offer in address (incl min fee)
                # first check if msc sell offer exists
                sell_offer_tx=None
                required_btc=0
                required_fee=0
                c=0 # default is mastercoin
                try:
                    sell_offer_tx=addr_dict[address][0][11][0]
                except (IndexError,KeyError):
                    pass
                if sell_offer_tx == None:
                    # if not, then maybe test mastercoins sell offer?
                    try:
                        sell_offer_tx=addr_dict[address][1][11][0]
                        c=1 # test mastercoins offer found
                    except (IndexError,KeyError):
                        pass
                # any relevant sell offer found?
                if sell_offer_tx != None:
                    info('bitcoin payment: '+t['tx_hash'])
                    info('for accept offer: '+sell_offer_tx['tx_hash'])
                    try:
                        required_btc=float(sell_offer_tx['formatted_bitcoin_amount_desired'])
                        required_fee=float(sell_offer_tx['formatted_fee_required'])
                        block_time_limit=int(sell_offer_tx['formatted_block_time_limit'])
                    except KeyError:
                        error('sell offer with missing details: '+sell_offer_tx['tx_hash'])
                    # now find the relevant accept and verify details (also partial purchase)
                    for sell_accept_tx in addr_dict[address][c]['accept_tx']: # go over all accepts
                        # now check if minimal amount, fee and block time limit are as required
                        sell_accept_block=int(sell_accept_tx['block'])
                        info('deal')
                        if amount >= required_btc and fee >= required_fee and sell_accept_block+block_time_limit <= current_block:
                            # mark deal as closed
                            info('closed')
                            spot_accept=addr_dict[address][c]['accept']
                            addr_dict[address][c]['balance']-=spot_accept      # reduce balance of seller
                            addr_dict[from_address][c]['balance']+=spot_accept # increase balance of buyer
                            addr_dict[from_address][c]['bought']+=spot_accept  # update bought
                            addr_dict[address][c]['sold']+=spot_accept         # update sold
                            addr_dict[address][c]['offer']-=spot_accept        # update offer
                            addr_dict[address][c]['accept']-=spot_accept       # update accept
                            # update bitcoin payment in accept tx
                            key=sell_accept_tx['tx_hash']
                            info('modify accept: '+key)
                            sell_accept_tx['btc_offer_txid']=key
                            if modified_tx_dict.has_key(key):
                                modified_tx_dict[key].append(sell_accept_tx)
                            else:
                                modified_tx_dict[key]=[sell_accept_tx]
                            return True # hidden assumption: payment is for a single accept

                        else:
                            debug('payment does not fit to accept: '+sell_accept_tx['tx_hash'])
    return False


# A fresh initialized address entry
def new_addr_entry():
    entry={}
    # for each currency
    for c in coins_list:
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


# update the main address database
# example call:
# update_addr_dict('1address', True, 'Mastercoin', balance=10, bought=2, bought_tx=t)
# accomulate True means add on top of previous values
# accomulate False means replace previous values
def update_addr_dict(addr, accomulate, *arguments, **keywords):

        # update specific currency fields within address
        # address is first arg
        # currency is second arg:
        # 'Mastercoin', 'Test Mastercoin' or 'exodus' for exodus purchases
        # then come the keywords and values to be updated
        c=arguments[0]
        if c!='Mastercoin' and c!='Test Mastercoin' and c!='exodus':
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
                else:
                    addr_dict[addr][c][kw]+=int(keywords[kw])
            else:
                if kw.endswith('_tx'): # replace the tx or value
                    addr_dict[addr][c][kw]=[keywords[kw]]
                else:
                    addr_dict[addr][c][kw]=int(keywords[kw])


def update_icon_details(t):
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
    return t

def mark_tx_invalid(tx_hash, reason):
    # mark tx as invalid
    tmp_dict=load_dict_from_file('tx/'+tx_hash+'.json')
    if int(tmp_dict['block']) < last_exodus_bootstrap_block:
        debug('skip invalidating exodus tx '+tx_hash+' and reason '+reason)
    else:
        tmp_dict['invalid']=(True,reason)
        atomic_json_dump(tmp_dict,'tx/'+tx_hash+'.json')

# go over modified tx and update the required tx + create bids json
def update_modified_tx_and_bids():

    # update sell/accept tx files
    # FIXME: make sure modifications include alarms
    for tx_hash in modified_tx_dict.keys():
        # get tx dict
        tmp_sell_dict=load_dict_from_file('tx/'+tx_hash+'.json','r')

        # update orig tx (status?)
        updated_tx=[tmp_sell_dict]

        # update bids
        bids=[]

        # go over all related tx
        for t in modified_tx_dict[tx_hash]:
            # add bid tx to sell offer
            bids.append(t)
            # update purchase accepts
            tmp_accept_dict=load_dict_from_file('tx/'+t['tx_hash']+'.json')
            for k in t.keys():
                # run over with new value
                tmp_accept_dict[k]=t[k]
            # write updated accept tx
            atomic_json_dump(tmp_accept_dict, 'tx/'+t['tx_hash']+'.json')

        # write updated bids
        atomic_json_dump(bids, 'bids/bids-'+tx_hash+'.json', add_brackets=False)


# generate api json
# address
# general files (10 in a page)
# mastercoin_verify
def generate_api_jsons():

    # create file for each address
    for addr in addr_dict.keys():
        addr_dict_api={}
        addr_dict_api['address']=addr
        for c in coins_list:
            sub_dict={}
            sub_dict['received_transactions']=addr_dict[addr][c]['in_tx']
            sub_dict['received_transactions'].reverse()
            sub_dict['sent_transactions']=addr_dict[addr][c]['out_tx']
            sub_dict['sent_transactions'].reverse()
            sub_dict['total_received']=from_satoshi(addr_dict[addr][c]['received'])
            sub_dict['total_sent']=from_satoshi(addr_dict[addr][c]['sent'])
            sub_dict['balance']=from_satoshi(addr_dict[addr][c]['balance'])
            sub_dict['exodus_transactions']=addr_dict[addr][c]['exodus_tx']
            sub_dict['exodus_transactions'].reverse()
            sub_dict['total_exodus']=from_satoshi(addr_dict[addr]['exodus']['bought'])
            addr_dict_api[coins_dict[c]]=sub_dict
        atomic_json_dump(addr_dict_api, 'addr/'+addr+'.json', add_brackets=False)

    # create files for msc and files for test_msc
    chunk=10
    sorted_currency_tx_list['Mastercoin'].reverse()
    sorted_currency_tx_list['Test Mastercoin'].reverse()

    # create the latest transactions pages
    pages={'Mastercoin':0, 'Test Mastercoin':0}
    for c in coins_list:
        for i in range(len(sorted_currency_tx_list[c])/chunk):
            atomic_json_dump(sorted_currency_tx_list[c][i*chunk:(i+1)*chunk], \
                'general/'+coins_short_name_dict[c]+'_'+'{0:04}'.format(i+1)+'.json', add_brackets=False)
            pages[c]+=1
    values_list=load_dict_from_file('www/values.json', all_list=True)
    updated_values_list=[]
    for v in values_list:
        v['pages']=pages[coins_reverse_short_name_dict[v['currency']]]
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
        tx_dict={}
        tx_list=[]
        for c in coins_list:
            for t in addr_dict[addr][c]['exodus_tx']+addr_dict[addr][c]['in_tx']+addr_dict[addr][c]['out_tx']:
                if t['invalid']==False:
                    tx_dict[t['tx_hash']]=True
                else:
                    tx_dict[t['tx_hash']]=False
        # collect all unique entries
        for key, value in tx_dict.iteritems():
            tx_list.append({'tx_hash':key, 'valid':value})
        mastercoin_verify_tx_per_address={'address':addr, 'transactions':tx_list}
        atomic_json_dump(mastercoin_verify_tx_per_address, 'mastercoin_verify/transactions/'+addr, add_brackets=False)     
        

# validate a matercoin transaction
def check_mastercoin_transaction(t):

    # update icon and details
    t=update_icon_details(t)

    # get general data from tx
    to_addr=t['to_address']
    from_addr=t['from_address']
    amount_transfer=to_satoshi(t['formatted_amount'])
    currency=t['currency_str']
    tx_hash=t['tx_hash']

    if from_addr == 'exodus': # assume exodus does not do sell offer/accept
        # exodus purchase
        update_addr_dict(to_addr, True, 'Mastercoin', balance=amount_transfer, exodus_tx=t)
        update_addr_dict(to_addr, True, 'Test Mastercoin', balance=amount_transfer, exodus_tx=t)
        update_addr_dict(to_addr, True, 'exodus', bought=amount_transfer)
        # exodus bonus - 10% for exodus (available slowly during the years)
        ten_percent=int((amount_transfer+0.0)/10+0.5)
        update_addr_dict(exodus_address, True, 'Mastercoin', balance=ten_percent, exodus_tx=t)
        update_addr_dict(exodus_address, True, 'Test Mastercoin', balance=ten_percent, exodus_tx=t)

        # tx belongs to mastercoin and test mastercoin
        for c in coins_list:
            sorted_currency_tx_list[c].append(t)
        return True 
    else:
        c=currency
        if c!='Mastercoin' and c!='Test Mastercoin':
            debug('unknown currency '+currency+ ' in tx '+tx_hash)
            return False
        # left are normal transfer and sell offer/accept
        if t['tx_type_str']==transaction_type_dict['00000000']:
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
                    # update msc list
                    sorted_currency_tx_list[c].append(t)
                    return True
        else:
            # sell offer
            if t['tx_type_str']==transaction_type_dict['00000014']:
                debug('sell offer: '+tx_hash)
                # sell offer from empty or non existing address is allowed
                # update details of sell offer
                # update single allowed tx for sell offer
                # add to list to be shown on general
                offer_amount=float(t['formatted_amount'])
                update_addr_dict(from_addr, True, c, offer=offer_amount, offer_tx=t)
                sorted_currency_tx_list[c].append(t)
                return True
            else:
                # sell accept
                if t['tx_type_str']==transaction_type_dict['00000016']:
                    debug('sell accept: '+tx_hash)
                    # verify corresponding sell offer exists and partial balance
                    # partially fill and update balances and sell offer
                    # add to list to be shown on general
                    # partially fill according to spot offer
                    accept_amount=float(t['formatted_amount'])
                    #update_addr_dict(from_addr, True, c, accept=accept_amount, accept_tx=t)
                    try:
                        sell_offer=addr_dict[to_addr][c]['offer']              # get orig offer from seller
                        sell_offer_tx=addr_dict[to_addr][c]['offer_tx'][-1] # get orig offer tx (last) from seller
                    except (KeyError, IndexError):
                        # offer from wallet without entry (empty wallet)
                        info('accept offer from missing seller '+to_addr)
                        mark_tx_invalid(tx_hash, 'accept offer of missing sell offer')
                        return False
                    try:
                        available=addr_dict[from_addr][c]['balance']    # get balance of that currency of buyer
                    except (KeyError, IndexError):
                        available=0
                    try:
                        formatted_price_per_coin=sell_offer_tx['formatted_price_per_coin']
                    except KeyError:
                        formatted_price_per_coin='price missing'
                    t['formatted_price_per_coin']=formatted_price_per_coin
                    try:
                        bitcoin_required=sell_offer_tx['formatted_bitcoin_amount_desired']
                    except KeyError:
                        bitcoin_required='missing required btc'
                    t['bitcoin_required']=bitcoin_required
                    t['sell_offer_txid']=sell_offer_tx['tx_hash']
                    t['btc_offer_txid']='unknown'

                    spot_offer=min(sell_offer,available)        # limited by available balance of seller
                    spot_accept=min(spot_offer,accept_amount)   # deal is limited by amount accepted by buyer
                    if spot_accept > 0: # ignore 0 or negative accepts
                        t['spot_accept']=spot_accept
                        t['payment_done']=False
                        t['payment_expired']=False
                        payment_timeframe=int(sell_offer_tx['formatted_block_time_limit'])
                        add_alarm(t,payment_timeframe)
                        update_addr_dict(from_addr, True, c, accept=spot_accept, accept_tx=t)
                    else:
                        debug('non positive spot accept')
                    # add to current bids (which appear on seller tx)
                    key=sell_offer_tx['tx_hash']
                    if modified_tx_dict.has_key(key):
                        modified_tx_dict[key].append(t)
                    else:
                        modified_tx_dict[key]=[t]
                    sorted_currency_tx_list[c].append(t)    # add per currency tx
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

    info('starting validation process')

    # get all tx sorted
    sorted_tx_list=get_sorted_tx_list()

    # use an artificial empty last tx with last height as a trigger for alarm check
    last_height=get_last_height()
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
                check_mastercoin_transaction(t)
            else: # maybe bitcoin payment
                if check_bitcoin_payment(t):
                    continue
                else: # report reason for invalid tx
                   debug(str(t['invalid'])+' '+t['tx_hash'])

        except OSError:
            error('error on tx '+t['tx_hash'])

    # update changed tx and create json for bids
    update_modified_tx_and_bids()

    # generate address pages and last tx pages
    generate_api_jsons()

    info('validation done')

if __name__ == "__main__":
    validate()
