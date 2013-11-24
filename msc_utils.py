#!/usr/bin/python
import subprocess
import json
import simplejson
import math
import hashlib
import inspect
import time
import git
import os
import msc_globals

from ecdsa import curves, ecdsa
# taken from https://github.com/warner/python-ecdsa
from pycoin import encoding
# taken from https://github.com/richardkiss/pycoin


__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

exodus_address='1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P'
first_exodus_bootstrap_block=249498
last_exodus_bootstrap_block=255365
exodus_bootstrap_deadline=1377993600
currency_type_dict={'00000001':'Mastercoin','00000002':'Test Mastercoin'}
transaction_type_dict={'00000000':'Simple send', '00000014':'Sell offer', '00000016':'Sell accept'}
multisig_simple_disabled=True
multisig_disabled=False
dust_limit=5430
MAX_PUBKEY_IN_BIP11=3
MAX_COMMAND_TRIES=3
LAST_BLOCK_NUMBER_FILE='last_block.txt'

def run_command(command, input_str=None, ignore_stderr=False):
    if ignore_stderr:
        if input_str!=None:
            p = subprocess.Popen(command, shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            return p.communicate(input_str)
        else:
            p = subprocess.Popen(command, shell=True,
                stdout=subprocess.PIPE)
            return p.communicate()
    else:
        if input_str!=None:
            p = subprocess.Popen(command, shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            return p.communicate(input_str)
        else:
            p = subprocess.Popen(command, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            return p.communicate()

def get_last_height():
    out, err = run_command("sx fetch-last-height")
    if err != None:
        return err
    else:
        return out.strip()

def get_block_timestamp(height):
    print height
    raw_block, err = run_command("sx fetch-block-header "+str(height))
    if err != None or raw_block == None:
        return (None, err)
    else:
        block_details, err = run_command("sx showblkhead", raw_block)
        if err != None or block_details == None:
            return (None, err)
        else:
            lines=block_details.split('\n')
            if len(lines)>0:
                for line in lines:
                    if line.startswith('timestamp:'):
                        timestamp=int(line.split('timestamp: ')[1])
                        return (timestamp, None)
                else:
                    return (None, "empty block details")

def get_raw_tx(tx_hash):
    out, err = run_command("sx fetch-transaction "+tx_hash)
    if err != None:
        return err
    else:
        return out

def get_json_tx(raw_tx, tx_hash='unknown hash'):
    parsed_json_tx=None
    for i in range(MAX_COMMAND_TRIES): # few tries
        json_tx, err = run_command("sx showtx -j", raw_tx)
        if err != None or json_tx == None:
            if i == MAX_COMMAND_TRIES:
                error(str(json_tx)+' '+str(tx_hash))
        else:
            try:
                parsed_json_tx=simplejson.JSONDecoder().decode(json_tx)
                break
            except simplejson.JSONDecodeError:
                if i == MAX_COMMAND_TRIES:
                    error(str(json_tx)+' '+str(tx_hash))
    return parsed_json_tx

def get_tx(tx_hash):
    raw_tx=get_raw_tx(tx_hash)
    return get_json_tx(raw_tx, tx_hash)

def get_tx_index(tx_hash):
    out, err = run_command("sx fetch-transaction-index "+tx_hash)
    if err != None:
        error(err)
    else:
        try:
            s=out.split()
            height=s[1]
            index=s[3]
            return(height,index)
        except IndexError:
            return (-1,-1)

def get_json_history(addr):
    out, err = run_command("sx history -j "+addr)
    if err != None:
        return err
    else:
        return out

def get_history(addr):
    parsed_json_history=None
    json_history=get_json_history(addr)
    try:
        parsed_json_history=simplejson.JSONDecoder().decode(json_history)
    except simplejson.JSONDecodeError:
        error('error parsing json_history')
    return parsed_json_history

# used as a key function for sorting history
def output_height(item):
    return item['output_height']

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

def get_pubkey(addr):
    out, err = run_command("sx get-pubkey "+addr)
    if err != None:
        return err
    else:
        return out.strip('\n')

def pubkey(key):
    out, err = run_command("sx pubkey ",key)
    # the only possible error is "Invalid private key."
    if out.strip('\n') == "Invalid private key.":
        return None
    else:
        return out.strip('\n')


def get_utxo(addr, value):
    out, err = run_command("sx get-utxo "+addr+" "+str(value))
    if err != None:
        return err
    else:
        return out

def rawscript(script):
    out, err = run_command("sx rawscript "+script)
    if err != None:
        return err
    else:
        return out.strip('\n')

def mktx(inputs_outputs):
    out, err = run_command("sx mktx "+inputs_outputs, None, True)
    # ignore err
    return out

def get_addr_from_key(key): # private or public key
    out, err = run_command("sx addr ", key)
    return out.strip('\n')

def error(msg):
    last_block_msg=''
    func_name='unknown'
    try:
        func_name=inspect.stack()[1][3]
    except IndexError:
        pass
    # on parse: update last block
    if func_name=='parse':
        # store last block
        try:
            f=open(LAST_BLOCK_NUMBER_FILE,'w')
            f.write(str(msc_globals.last_block)+'\n')
            f.close()
            last_block_msg=' ('+str(msc_globals.last_block)+')'
        except IOError:
            pass
    print '[E] '+func_name+': '+str(msg)+last_block_msg
    exit(1)

def info(msg):
    func_name='unknown'
    try:
        func_name=inspect.stack()[1][3]
    except IndexError:
        pass
    print '[I] '+func_name+': '+str(msg)

def debug(msg):
    if msc_globals.d == True:
        func_name='unknown'
        try:
            func_name=inspect.stack()[1][3]
        except IndexError:
            pass
        print '[D] '+func_name+': '+str(msg)

def bootstrap_dict_per_tx(block, tx_hash, address, value, dacoins):
    tx_dict={"block": str(block), "tx_hash": tx_hash, "currency_str": "Mastercoin and Test Mastercoin", "to_address": address, "from_address": "exodus", "exodus": True, "tx_method_str": "exodus", "orig_value":value ,"formatted_amount": from_satoshi(dacoins), "tx_type_str": "exodus"}
    return tx_dict

def formatted_decimal(float_number):
    s=str("{0:.8f}".format(float_number))
    if s.strip('0.') == '':      # only zero and/or decimal point
        return '0.0'
    else:
        trimmed=s.rstrip('0')     # remove zeros on the right
        if trimmed.endswith('.'): # make sure there is at least one zero on the right
            return trimmed+'0'
        else:
            if trimmed.find('.')==-1:
                return trimmed+'.0'
            else:
                return trimmed

def to_satoshi(value):
    return int(float(value)*100000000+0.5)

def from_satoshi(value):
    float_number=int(value)/100000000.0
    return formatted_decimal(float_number)

def from_hex_satoshi(value):
    float_number=int(value,16)/100000000.0
    return formatted_decimal(float_number)

def b58encode(v):
  """ encode v, which is a string of bytes, to base58.
"""

  long_value = 0L
  for (i, c) in enumerate(v[::-1]):
    long_value += (256**i) * ord(c)

  result = ''
  while long_value >= __b58base:
    div, mod = divmod(long_value, __b58base)
    result = __b58chars[mod] + result
    long_value = div
  result = __b58chars[long_value] + result

  # Bitcoin does a little leading-zero-compression:
  # leading 0-bytes in the input become leading-1s
  nPad = 0
  for c in v:
    if c == '\0': nPad += 1
    else: break

  return (__b58chars[0]*nPad) + result


def b58decode(v, length):
    """ decode v into a string of len bytes
    """
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
      long_value += __b58chars.find(c) * (__b58base**i)

    result = ''
    while long_value >= 256:
      div, mod = divmod(long_value, 256)
      result = chr(mod) + result
      long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
      if c == __b58chars[0]: nPad += 1
      else: break

    result = chr(0)*nPad + result
    if length is not None and len(result) != length:
      return None

    return result


def hash_160_to_bc_address(h160):
    vh160 = "\x00"+h160  # \x00 is version 0
    h3=hashlib.sha256(hashlib.sha256(vh160).digest()).digest()
    addr=vh160+h3[0:4]
    return b58encode(addr)

def bc_address_to_hash_160(addr):
    vh160_with_checksum=b58decode(addr, 25)
    return vh160_with_checksum[1:-4]

def get_sha256(string):
    return hashlib.sha256(string).hexdigest()

def is_script_output(output):
    # check that the script looks like:
    # 1 [ hex ] ...
    return output.startswith('1 [ ')

def is_script_multisig(output):
    # check that the script looks like:
    # 1 [ pubkey1 ] .. [ hex ] [ 2 of 3 ] checkmultisig
    return is_script_output(output) and output.endswith('checkmultisig')

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

def parse_simple_basic(tx, tx_hash='unknown', after_bootstrap=True):
    json_tx=get_json_tx(tx)
    outputs_list=json_tx['outputs']
    (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)=examine_outputs(outputs_list)
    num_of_outputs=len(outputs_list)

    # collect all "from addresses" (normally only a single one)
    from_address=''
    try:
        inputs=json_tx['inputs']
        for i in inputs:
            if i['address'] != None:
                if from_address != '':
                    from_address+=';'
                from_address+=i['address']
            else:
                from_address='not signed'

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
            if after_bootstrap: # bitcoin payments are possible
                info('bitcoin payment tx (different output values) '+tx_hash)
                return parse_bitcoin_payment(tx, tx_hash)
            else:
                info('invalid mastercoin tx (different output values) '+tx_hash)
                return {'invalid':(True,'different output values'), 'tx_hash':tx_hash}

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

        if(len(seq_list)==3):
            # If there is a perfect sequence (i.e. 3,4,5), mark invalid
            if (seq_list[seq_start_index]+1)%256==(seq_list[(seq_start_index+1)%3])%256 and \
                (seq_list[(seq_start_index-1)%3]+1)%256==(seq_list[seq_start_index])%256:
                info('invalid mastercoin tx (perfect sequence '+str(seq_list)+') '+tx_hash)
                return {'invalid':(True,'perfect sequence '+str(seq_list)), 'tx_hash':tx_hash}

            # If there is an ambiguous sequence (i.e. 3,4,4), mark invalid
            if seq_list[seq_start_index]==seq_list[(seq_start_index+2)%3] or \
                seq_list[(seq_start_index+1)%3]==seq_list[(seq_start_index+2)%3] or \
                seq_list[(seq_start_index)]==seq_list[(seq_start_index+1)%3]:
                info('invalid mastercoin tx (ambiguous sequence '+str(seq_list)+') '+tx_hash)
                return {'invalid':(True,'ambiguous sequence '+str(seq_list)), 'tx_hash':tx_hash}

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
    except KeyError, IndexError:
        info('invalid mastercoin tx '+tx_hash)
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
    (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)=examine_outputs(all_outputs, tx_hash)
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
                    parse_dict['formatted_bitcoin_amount_desired']= formatted_decimal(bitcoin_amount_desired)
                    parse_dict['formatted_price_per_coin']= formatted_decimal(price_per_coin)
                    parse_dict['formatted_block_time_limit']= str(int(data_dict['block_time_limit'],16))

                if data_dict['transactionType'] == '00000016': # Sell accept
                    # remove irrelevant keys
                    parse_dict.pop('bitcoin_amount_desired', None)
                    parse_dict.pop('block_time_limit', None)
                    # add place holders
                    parse_dict['bitcoin_required'] = 'not_yet_calculated'
                    parse_dict['sell_offer_txid'] = 'not_yet_checked'
                    parse_dict['payment_txid'] = 'not_yet_checked'
                    parse_dict['status'] = 'not_yet_checked'

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

def examine_outputs(outputs_list, tx_hash='unknown'):
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
        # to 1EXoDus, or have 1EXoDus as change address)
        if len(outputs_to_exodus) != 1:
            error("not implemented tx with multiple 1EXoDus outputs: "+tx_hash)
        return (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)

def get_tx_method(tx, tx_hash='unknown'): # multisig_simple, multisig, multisig_invalid, basic
        json_tx=get_json_tx(tx)
        outputs_list=json_tx['outputs']
        (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)=examine_outputs(outputs_list, tx_hash)
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

def sign(tx, priv_key, inputs):
    info('signing tx')
    addr=get_addr_from_key(priv_key)
    hash160=bc_address_to_hash_160(addr).encode('hex_codec')
    prevout_script=rawscript('dup hash160 [ '+hash160 + ' ] equalverify checksig')
    # save tx to a temporary file
    # FIXME: find a more secure way that does not involve filesystem
    f=open('txfile.tx','w')
    f.write(tx)
    f.close()
    try:
        # assumtion: that all inputs come from the same address (required in spec)
        n=0;
        for i in inputs:
            signature=run_command('sx sign-input txfile.tx '+str(n)+' '+prevout_script, priv_key)[0].strip('\n')
            signed_rawscript=rawscript('[ '+signature +' ] [ '+pubkey(priv_key)+' ]')
            signed_tx=run_command('sx set-input txfile.tx '+str(n), signed_rawscript)
            n+=1
            # replace the file with the signed one
            f=open('txfile.tx','w')
            f.write(signed_tx[0].strip('\n'))
            f.close()
    except IndexError:
        error('failed parsing inputs for signing')
    return signed_tx[0].strip('\n')

def validate_sig(filename, index, script_code, signature):
    out, err = run_command('sx validsig '+filename+' '+str(index)+' '+script_code+' '+signature)
    if err != None:
        return err
    else:
        return out

def validate_tx(filename):
    out, err = run_command('sx validtx '+filename)
    if err != None:
        return err
    else:
        return out.strip('\n')

def send_tx(filename, host='localhost', port=8333):
    out, err = run_command("sx sendtx "+filename+' '+host+' '+port)
    if err != None:
        return err
    else:
        info('sent')
        return None

def broadcast_tx(filename):
    out, err = run_command("sx broadcast-tx "+filename)
    if err != None:
        return err
    else:
        info('broadcasted')
        return None

def format_time_from_struct(st, short=False):
    if short:
        return time.strftime('%Y%m%d',st)
    else:
        return time.strftime('%d %b %Y %H:%M:%S GMT',st)

def format_time_from_epoch(epoch, short=False):
    return format_time_from_struct(time.localtime(int(epoch)), short)

def get_git_details(directory="~/mastercoin-tools"):
    repo = git.Repo(directory)
    assert repo.bare == False
    head_commit=repo.head.commit
    timestamp=format_time_from_epoch(int(head_commit.authored_date), True)
    return(head_commit.hexsha,timestamp)

def archive_repo(directory="~/mastercoin-tools"):
    (commit_hexsha, timestamp)=get_git_details()
    assert repo.bare == False
    archive_name='www/downloads/mastercoin-tools-src-'+timestamp+'-'+commit_hexsha[:8]+'-'+timestamp+'.tar'
    repo = git.Repo(directory)
    repo.archive(open(archive_name,'w'))

def archive_parsed_data(directory="~/mastercoin-tools"):
    (commit_hexsha, timestamp)=get_git_details()
    archive_name='www/downloads/mastercoin-tools-parse-snapshot-'+timestamp+'-'+commit_hexsha[:8]+'.tar.gz'
    path_to_archive='www/revision.json www/tx www/addr www/general/'
    out, err = run_command("tar cz "+path_to_archive+" -f "+archive_name)
    if err != None:
        return err
    else:
        return out

def get_now():
    return format_time_from_struct(time.gmtime())

def get_today():
    return format_time_from_struct(time.gmtime(), True)

def get_revision_dict(last_block):
    rev={}
    git_details=get_git_details()
    hexsha=git_details[0]
    commit_time=git_details[1]
    rev['commit_hexsha']=hexsha
    rev['commit_time']=commit_time
    rev['url']='https://github.com/grazcoin/mastercoin-tools/commit/'+hexsha
    rev['last_parsed']=get_now()
    rev['last_block']=last_block
    return rev

def is_pubkey_valid(pubkey):
    sec=encoding.binascii.unhexlify(pubkey)
    public_pair=encoding.sec_to_public_pair(sec)
    return curves.ecdsa.point_is_valid(ecdsa.generator_secp256k1, public_pair[0], public_pair[1])

def get_compressed_pubkey_format(pubkey):
    public_pair=encoding.sec_to_public_pair(encoding.binascii.unhexlify(pubkey))
    return encoding.binascii.hexlify(encoding.public_pair_to_sec(public_pair))

def get_address_of_pubkey(pubkey):
    public_pair=encoding.sec_to_public_pair(encoding.binascii.unhexlify(pubkey))
    return encoding.public_pair_to_bitcoin_address(public_pair)

def get_address_from_output(tx_and_number):
    try:
        tx_hash=tx_and_number.split(':')[0]
        number=int(tx_and_number.split(':')[1])
    except IndexError:
        return None
    rawtx=get_raw_tx(tx_hash)
    json_tx=get_json_tx(rawtx)
    if json_tx == None:
        error('failed getting json_tx (None) for '+tx_hash)
    all_outputs=json_tx['outputs']
    output=all_outputs[number]
    return output['address']

def get_value_from_output(tx_and_number):
    try:
        txid=tx_and_number.split(':')[0]
        number=int(tx_and_number.split(':')[1])
    except IndexError:
        return None
    rawtx=get_raw_tx(txid)
    json_tx=get_json_tx(rawtx)
    try: 
        all_outputs=json_tx['outputs']
    except TypeError: # obelisk can give None
        error('bad outputs parsing on: '+json_tx)
    output=all_outputs[number]
    return output['value']

def get_nearby_valid_pubkey(pubkey):
    valid_pubkey=pubkey
    l=len(pubkey)
    while not is_pubkey_valid(valid_pubkey):
        info("trying "+valid_pubkey)
        next=hex(int(valid_pubkey, 16)+1).strip('L').split('0x')[1]
        valid_pubkey = next.zfill(l)
    info("valid  "+valid_pubkey)
    return valid_pubkey

def get_string_xor(s1,s2):
    result = int(s1, 16) ^ int(s2, 16)
    return '{:x}'.format(result)

def load_dict_from_file(filename, all_list=False, skip_error=False):
    tmp_dict={}
    try:
        f=open(filename,'r')
        if all_list == False:
            tmp_dict=json.load(f)[0]
        else:
            tmp_dict=json.load(f)
        f.close()
    except IOError: # no such file?
        if skip_error:
            info('dict load failed. missing '+filename)
        else:
            error('dict load failed. missing '+filename)
    return tmp_dict

# mkdir -p function
def mkdirp(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)

# dump json to a file, and replace it atomically
def atomic_json_dump(tmp_dict, filename, add_brackets=True):
    # check if filename already exists
    # if exists, write to a tmp file first
    # then move atomically

    # make sure path exists
    path, only_filename = os.path.split(filename)
    mkdirp(path)

    f=open(filename,'w')
    if add_brackets:
        f.write('[')
    f.write(json.dumps(tmp_dict, sort_keys=True))
    if add_brackets:
        f.write(']')
    f.write('\n')
    f.close()

