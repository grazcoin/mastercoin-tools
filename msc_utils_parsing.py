#!/usr/bin/python
from msc_utils_obelisk import *

currency_type_dict={'00000001':'Mastercoin','00000002':'Test Mastercoin'}
reverse_currency_type_dict={'Mastercoin':'00000001','Test Mastercoin':'00000002'}
transaction_type_dict={'00000000':'Simple send', '00000014':'Sell offer', '00000016':'Sell accept'}
exodus_address='1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P'
first_exodus_bootstrap_block=249498
last_exodus_bootstrap_block=255365
exodus_bootstrap_deadline=1377993600
multisig_simple_disabled=True
multisig_disabled=False
dust_limit=5430
MAX_PUBKEY_IN_BIP11=3
MAX_COMMAND_TRIES=3

# used as a key function for sorting outputs of msc tx
def get_dataSequenceNum(item):
    try:
        data_script=item['script'].split()[3].zfill(42)
        dataSequenceNum=data_script[2:4]
        return dataSequenceNum
    except KeyError, IndexError:
        return None

def get_currency_type_from_dict(currencyId):
    if currency_type_dict.has_key(currencyId):
        return currency_type_dict[currencyId]
    else:
        return 'Unknown currency id '+str(currencyId)

def get_transaction_type_from_dict(transactionType):
    if transaction_type_dict.has_key(transactionType):
        return transaction_type_dict[transactionType]
    else:
        return 'Unknown transaction type '+str(transactionType)

def bootstrap_dict_per_tx(block, tx_hash, address, value, dacoins):
    tx_dict={"block": str(block), "tx_hash": tx_hash, "currency_str": "Mastercoin and Test Mastercoin", "to_address": address, "from_address": "exodus", "exodus": True, "tx_method_str": "exodus", "orig_value":value ,"formatted_amount": from_satoshi(dacoins), "tx_type_str": "exodus"}
    return tx_dict

def parse_data_script(data_script):
    parse_dict={}
    if len(data_script)<42:
        info('invalid data script '+data_script.encode('hex_codec'))
        return parse_dict
    parse_dict['baseCoin']=data_script[0:2] # 00 for normal bitcoin (different for multisig?)
    parse_dict['dataSequenceNum']=data_script[2:4]
    parse_dict['transactionType']=data_script[4:12]
    parse_dict['currencyId']=data_script[12:20]
    parse_dict['amount']=data_script[20:36]
    parse_dict['bitcoin_amount_desired']=data_script[36:52]
    parse_dict['block_time_limit']=data_script[52:54]
    return parse_dict

def parse_2nd_data_script(data_script):
    parse_dict={}
    if len(data_script)<42:
        info('invalid data script '+data_script.encode('hex_codec'))
        return parse_dict
    parse_dict['fee_required']=data_script[4:10]
    return parse_dict

def parse_bitcoin_payment(tx, tx_hash='unknown'):
    json_tx=get_json_tx(tx)
    outputs_list=json_tx['outputs']
    
    from_address=''
    to_address=''
    total_inputs=0
    total_outputs=0
    try:
        inputs=json_tx['inputs']
        for i in inputs:
            if i['address'] != None:
                if from_address != '':
                    from_address+=';'
                from_address+=i['address']
            else:
                from_address='not signed'
            total_inputs+=get_value_from_output(i['previous_output'])
    except KeyError, IndexError:
        error('inputs error')
    try:
        for o in outputs_list:
            if o['address'] != None:
                if to_address != '':
                    to_address+=';'
                to_address+=o['address']+':'+from_satoshi((o['value']))
            total_outputs+=(o['value'])
    except KeyError, IndexError:
        error('outputs error')

    parse_dict={}
    parse_dict['from_address']=from_address
    parse_dict['to_address']=to_address
    parse_dict['fee']=from_satoshi(total_inputs-total_outputs)
    parse_dict['tx_hash']=tx_hash
    parse_dict['invalid']=(True,'bitcoin payment')
    return parse_dict

# note: outputs_list_no_exodus must be sorted by seq number
def peek_and_decode(outputs_list_no_exodus, different_outputs_values):
    # there are 1 or 2 output values
    # remove change (in the case that there are 2)
    change=None
    for value in different_outputs_values.keys():
        if len(different_outputs_values[value])==1:
            # this is the change
            change=different_outputs_values[value][0]
            break
    outputs=[]
    if change != None:
        for o in outputs_list_no_exodus:
            if o != change:
                outputs.append(o)
    else:
        outputs=outputs_list_no_exodus

    good_data=None
    good_reference=None
    maybe=0
    # check the outputs to see if one or more look like data
    l=len(outputs)
    for i in range(l):
        data=outputs[i]
        reference=outputs[(i+1)%l]
        data_script=data['script'].split()[3].zfill(42)
        if data_script[4:20]=='0000000000000001' \
            or data_script[4:20]=='0000000000000002':
            maybe+=1
            good_data=data
            good_reference=reference
    if maybe != 1: # permit only if one output looks like a data address
        found = False
    else:
        found = True
    return (found, good_data, good_reference)

def parse_simple_basic(tx, tx_hash='unknown', after_bootstrap=True):
    json_tx=get_json_tx(tx)
    outputs_list=json_tx['outputs']
    (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)=examine_outputs(outputs_list, tx_hash, tx)
    num_of_outputs=len(outputs_list)

    # collect all "from addresses" (normally only a single one)
    from_address=''
    try:
        inputs=json_tx['inputs']
        inputs_values_dict={}
        for i in inputs:
            input_value=get_value_from_output(i['previous_output'])
            input_address=i['address']
            if inputs_values_dict.has_key(input_address):
                inputs_values_dict[input_address]+=int(input_value)
            else:
                inputs_values_dict[input_address]=int(input_value)

        # the from address is the one with the highest value
        from_address=max(inputs_values_dict, key=inputs_values_dict.get)

        # sort outputs according to dataSequenceNum to find the reference (n) and data (n+1)
        outputs_list_no_exodus.sort(key=get_dataSequenceNum)
        # look for sequence of at least length 2 to find the reference address
        seq_list=[]
        for o in outputs_list_no_exodus:
            seq=get_dataSequenceNum(o)
            seq_list.append(int(seq,16))
        reference=None
        data=None
        seq_start_index=-1

        # validation of basic simple send transaction according to:
        # https://bitcointalk.org/index.php?topic=265488.msg3190175#msg3190175

        # all outputs has to be the same (except for change)
        if len(different_outputs_values) > 2:
            # last resort: let's try to peek and decode
            (found, data, reference)=peek_and_decode(outputs_list_no_exodus, different_outputs_values)
            if found:
                debug('different outputs resolved using peek and decode on '+tx_hash)
            else:
                if after_bootstrap: # bitcoin payments are possible
                    info('bitcoin payment tx (different output values) '+tx_hash)
                    return parse_bitcoin_payment(tx, tx_hash)
                else:
                    info('invalid mastercoin tx (different output values) '+tx_hash)
                    return {'invalid':(True,'different output values'), 'tx_hash':tx_hash}

        else:
            # currently support only the simple send (a single data packet)
            # if broken sequence (i.e. 3,4,8), then the odd-man-out is the change address
            for s in seq_list:
                if (s+1)%256 == int(seq_list[(seq_list.index(s)+1)%len(seq_list)]):
                    seq_start_index=seq_list.index(s)
                    data=outputs_list_no_exodus[seq_list.index(s)]
                    reference=outputs_list_no_exodus[(seq_list.index(s)+1)%len(seq_list)]

            # no change case:
            if(len(seq_list)==2):
                diff=abs(seq_list[0]-seq_list[1])
                if diff != 1 and diff != 255:
                    info('invalid mastercoin tx (non following 2 seq numbers '+str(seq_list)+') '+tx_hash)
                    return {'invalid':(True,'non following 2 seq numbers '+str(seq_list)), 'tx_hash':tx_hash}

            # handle special cases of perfect seq and ambiguous seq using 'peek and decode'
            found=True # may change only in one of the below special cases
            reason=''
            if(len(seq_list)==3):
                # If there is a perfect sequence (i.e. 3,4,5), try peek and decode
                if (seq_list[seq_start_index]+1)%256==(seq_list[(seq_start_index+1)%3])%256 and \
                    (seq_list[(seq_start_index-1)%3]+1)%256==(seq_list[seq_start_index])%256:
                    reason='perfect sequence '+str(seq_list)
                    
                # If there is an ambiguous sequence (i.e. 3,4,4), try peek and decode
                if seq_list[seq_start_index]==seq_list[(seq_start_index+2)%3] or \
                    seq_list[(seq_start_index+1)%3]==seq_list[(seq_start_index+2)%3] or \
                    seq_list[(seq_start_index)]==seq_list[(seq_start_index+1)%3]:
                    reason='ambiguous sequence '+str(seq_list)

                if reason != '': # one of the above special cases
                    (found, data, reference)=peek_and_decode(outputs_list_no_exodus, different_outputs_values)

        if not found:
            info('invalid mastercoin tx ('+reason+') '+tx_hash)
            return {'invalid':(True,reason), 'tx_hash':tx_hash}

        if reference==None:
            debug('could not find reference using seq numbers. trying peek and decode')
            (found, data, reference)=peek_and_decode(outputs_list_no_exodus, different_outputs_values)
            if not found:
                error('reference is None on '+tx_hash)

        to_address=reference['address']
        data_script=data['script'].split()[3].zfill(42)
        data_dict=parse_data_script(data_script)
        if len(data_dict) >= 6: # at least the basic 6 fields were parsed
            parse_dict=data_dict
            parse_dict['tx_hash']=tx_hash
            parse_dict['from_address']=from_address
            parse_dict['to_address']=to_address
            parse_dict['formatted_amount']=from_hex_satoshi(data_dict['amount'])
            parse_dict['currency_str']=get_currency_type_from_dict(data_dict['currencyId'])
            parse_dict['tx_type_str']=get_transaction_type_from_dict(data_dict['transactionType'])
            parse_dict['tx_method_str']='basic'
            # FIXME: checksum?
            return parse_dict
    except (KeyError, IndexError, TypeError) as e:
        info('invalid mastercoin tx ('+str(e)+') at tx '+tx_hash)
        return {'invalid':(True,'bad parsing'), 'tx_hash':tx_hash}

def parse_multisig_simple(tx, tx_hash='unknown'):
    if multisig_simple_disabled:
        info('multisig simple is disabled: '+tx_hash)
        return {}
    parsed_json_tx=get_json_tx(tx)
    script=parsed_json_tx['outputs'][1]['script']
    fields=script.split('[ ')
    change_address_pub=fields[1].split(' ]')[0]
    padded_recipientHex_and_dataHex=recipientHex=fields[2].split(' ]')[0]
    recipientHex=padded_recipientHex_and_dataHex[0:50]
    data_script=padded_recipientHex_and_dataHex[50:92]
    data_dict=parse_data_script(data_script)
    if len(data_dict) >= 6: # at least 6 basic fields got parse
        parse_dict=data_dict
        parse_dict['tx_hash']=tx_hash
        parse_dict['from_address'] = get_addr_from_key(change_address_pub)
        parse_dict['to_address'] = b58encode(recipientHex.decode('hex_codec'))
        parse_dict['formatted_amount'] = from_hex_satoshi(data_dict['amount'])
        parse_dict['currency_str'] = get_currency_type_from_dict(data_dict['currencyId'])
        parse_dict['tx_type_str'] = get_transaction_type_from_dict(data_dict['transactionType'])
        parse_dict['tx_method_str'] = 'multisig simple'
        return parse_dict
    else:
        error('Bad parsing of data script '+data_script.encode('hex_codec'))
        return {}

def parse_multisig(tx, tx_hash='unknown'):
    if multisig_disabled:
        info('multisig is disabled: '+tx_hash)
        return {}
    parsed_json_tx=get_json_tx(tx)
    parse_dict={}
    input_addr=''
    for i in parsed_json_tx['inputs']:
        previous_output=i['previous_output']
        if input_addr == '':
            input_addr=get_address_from_output(previous_output)
        else:
            if get_address_from_output(previous_output) != input_addr:
                error('Bad multiple inputs on: '+tx_hash)
                return {}
    all_outputs=parsed_json_tx['outputs']
    (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)=examine_outputs(all_outputs, tx_hash, tx)
    tx_dust=outputs_to_exodus[0]['value']
    dust_outputs=different_outputs_values[tx_dust]
    to_address='unknown'
    for o in dust_outputs: # assume the only other dust is to recipient
        if o['address']!=exodus_address:
            to_address=o['address']
            continue
    for o in outputs_list_no_exodus:
        if o['address']==None: # This should be the multisig
            script=o['script']
            # verify that it is a multisig
            if not script.endswith('checkmultisig'):
                error('Bad multisig data script '+script)
            fields=script.split('[ ')

            # more sanity checks on BIP11
            max_pubkeys=int(fields[-1].split()[-2])
            req_pubkeys=int(fields[0])
            if req_pubkeys != 1:
                info('error m-of-n with m different than 1 ('+str(req_pubkeys)+'). skipping tx '+tx_hash)
                return {'tx_hash':tx_hash, 'invalid':(True, 'error m-of-n with m different than 1')}
            if max_pubkeys < 2 or max_pubkeys > 3:
                info('error m-of-n with n out of range ('+str(max_pubkeys)+'). skipping tx '+tx_hash)
                return {'tx_hash':tx_hash, 'invalid':(True, 'error m-of-n with n out of range')}

            # parse the BIP11 pubkey list
            data_script_list=[]
            for i in range(MAX_PUBKEY_IN_BIP11-1):
                index=i+2 # the index of the i'th pubkey
                try:
                    data_script_list.append(fields[index].split(' ]')[0])
                except IndexError:
                    break

            # prepare place holder lists for obfus,deobfus,data_dict
            obfus_str_list=[]
            dataHex_deobfuscated_list=[]
            data_dict_list=[]
           
            if input_addr == None:
                info('none input address (BIP11 inputs are not supported yet)')
                return {'tx_hash':tx_hash, 'invalid':(True, 'not supported input (BIP11/BIP16)')}

            obfus_str_list.append(get_sha256(input_addr)) # 1st obfus is simple sha256
            for i in range(len(data_script_list)):
                if i<len(data_script_list)-1: # one less obfus str is needed (the first was not counted)
                    obfus_str_list.append(get_sha256(obfus_str_list[i].upper())) # i'th obfus is sha256 of upper prev
                dataHex_deobfuscated_list.append(get_string_xor(data_script_list[i][2:-2],obfus_str_list[i][:62]).zfill(64)+'00')

            # deobfuscated list is ready
            #info(dataHex_deobfuscated_list)

            try:
                data_dict=parse_data_script(dataHex_deobfuscated_list[0])
            except IndexError:
                error('cannot parse dataHex_deobfuscated_list')
            if len(data_dict) >= 6: # at least 6 basic fields got parse on the first dataHex
                amount=int(data_dict['amount'],16)/100000000.0
                parse_dict=data_dict
                parse_dict['tx_hash']=tx_hash
                parse_dict['formatted_amount'] = formatted_decimal(amount)
                parse_dict['currency_str'] = get_currency_type_from_dict(data_dict['currencyId'])
                parse_dict['tx_type_str'] = get_transaction_type_from_dict(data_dict['transactionType'])
                parse_dict['tx_method_str'] = 'multisig'

                if data_dict['transactionType'] == '00000000': # Simple send
                    # remove irrelevant keys
                    parse_dict.pop('bitcoin_amount_desired', None)
                    parse_dict.pop('block_time_limit', None)

                if data_dict['transactionType'] == '00000014': # Sell offer
                    bitcoin_amount_desired=int(data_dict['bitcoin_amount_desired'],16)/100000000.0
                    if amount > 0:
                        price_per_coin=bitcoin_amount_desired/amount
                    else:
                        price_per_coin=0
                        parse_dict['invalid']=(True,'non positive sell offer amount')
                    # duplicate with another name
                    parse_dict['formatted_amount_available'] = parse_dict['formatted_amount']
                    # format fields
                    parse_dict['formatted_bitcoin_amount_desired']= formatted_decimal(bitcoin_amount_desired)
                    parse_dict['formatted_price_per_coin']= formatted_decimal(price_per_coin)
                    parse_dict['formatted_block_time_limit']= str(int(data_dict['block_time_limit'],16))

                if data_dict['transactionType'] == '00000016': # Sell accept
                    # remove irrelevant keys
                    parse_dict.pop('bitcoin_amount_desired', None)
                    parse_dict.pop('block_time_limit', None)
                    # duplicate with another name
                    parse_dict['formatted_amount_requested'] = parse_dict['formatted_amount']
                    # add place holders
                    parse_dict['bitcoin_required'] = 'Not available'
                    parse_dict['sell_offer_txid'] = 'Not available'
                    parse_dict['payment_txid'] = 'Not available'
                    parse_dict['status'] = 'Awaiting payment'

                if len(dataHex_deobfuscated_list)>1: # currently true only for Sell offer
                    data_dict=parse_2nd_data_script(dataHex_deobfuscated_list[1])
                    for key in data_dict:
                        parse_dict[key]=data_dict[key]
                    parse_dict['formatted_fee_required'] = from_hex_satoshi(data_dict['fee_required'])

        else: # not the multisig output
            # the output with dust
            parse_dict['to_address']=o['address']

    if parse_dict == {}:
        error('Bad parsing of multisig: '+tx_hash)

    parse_dict['from_address']=input_addr
    parse_dict['to_address']=to_address
                
    return parse_dict

def examine_outputs(outputs_list, tx_hash, raw_tx):
        # if we're here, then 1EXoDus is within the outputs. Remove it, but ...
        outputs_list_no_exodus=[]
        outputs_to_exodus=[]
        different_outputs_values={}
        for o in outputs_list:
            if o['address']!=exodus_address:
                outputs_list_no_exodus.append(o)
            else:
                outputs_to_exodus.append(o)
            output_value=o['value']
            if different_outputs_values.has_key(output_value):
                different_outputs_values[output_value].append(o)
            else:
                different_outputs_values[output_value]=[o]
        # take care if multiple 1EXoDus exist (for the case that someone sends msc
        # to 1EXoDus, or have 1EXoDus as change address, or sends from 1EXoDus)
        if len(outputs_to_exodus) != 1:
            # support the special case of sending from 1EXoDus
            json_tx=get_json_tx(raw_tx)
            inputs_list=json_tx['inputs']
            from_exodus=False
            for i in inputs_list:
                if i['address']==exodus_address:
                    from_exodus=True
                    break
            if not from_exodus:
                error("not implemented tx with multiple 1EXoDus outputs not from 1EXoDus: "+tx_hash)
            else: # 1EXoDus has sent this tx
                # Maximal 2 values are valid (dust and change)
                if len(different_outputs_values.keys()) > 2:
                    error("tx sent by exodus with more than 2 different values: "+tx_hash)
                # move the dust exodus from outputs_to_exodus list to the outputs_list_no_exodus one
                if len(different_outputs_values.keys()) == 1: # change is identical to marker
                    debug("tx sent by exodus with single value")
                    # move one item from exodus to no exodus list
                    o=outputs_to_exodus.pop()
                    outputs_list_no_exodus.append(o)
                else:
                    debug("tx sent by exodus with 2 values to exodus")
                    # as there is a signle change, dust_value belongs to list with non single item
                    output_values=different_outputs_values.keys()
                    if len(different_outputs_values[output_values[0]])==1:
                        dust_value=output_values[1]
                    else:
                        dust_value=output_values[0]
                    # move the dust item from exodus to no exodus list
                    dust_outputs_to_exodus=[]
                    non_dust_outputs_to_exodus=[]
                    for o in outputs_to_exodus:
                        if o['value']==dust_value:
                            dust_outputs_to_exodus.append(o)
                        else:
                            non_dust_outputs_to_exodus.append(o)
                    # move the item
                    outputs_list_no_exodus+=[dust_outputs_to_exodus[0]]
                    outputs_to_exodus=non_dust_outputs_to_exodus+dust_outputs_to_exodus[1:]
        return (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)

def get_tx_method(tx, tx_hash='unknown'): # multisig_simple, multisig, multisig_invalid, basic
        json_tx=get_json_tx(tx)
        outputs_list=json_tx['outputs']
        (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)=examine_outputs(outputs_list, hx_hash, tx)
        num_of_outputs=len(outputs_list)

        # check if basic or multisig
        is_basic=True
        for o in outputs_list:
            if is_script_multisig(o['script']):
                if num_of_outputs == 2:
                    return 'multisig_simple'
                else:
                    if num_of_outputs > 2:
                        return 'multisig'
                    else:
                        return 'multisig_invalid'
        # all the rest, which includes exodus and invalids are considered as basic
        return 'basic'
