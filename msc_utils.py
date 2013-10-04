#!/usr/bin/python
import subprocess
import json
import simplejson
import math
import hashlib
import inspect

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

exodus_address='1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P'
first_exodus_bootstrap_block=249498
last_exodus_bootstrap_block=255365
exodus_bootstrap_deadline=1377993600
currency_type_dict={'00000001':'Mastercoin','00000002':'Test Mastercoin'}
transaction_type_dict={'00000000':'Simple send'}
dust_limit=5430

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

def get_block_timestamp(height):
    raw_block, err = run_command("sx fetch-block-header "+str(height))
    if err != None:
        return err
    else:
        block_details, err = run_command("sx showblkhead", raw_block)
        if err != None:
            return err
        else:
            for line in block_details.split('\n'):
                if line.startswith('timestamp:'):
                    timestamp=int(line.split('timestamp: ')[1])
                    return timestamp

def get_raw_tx(tx_hash):
    out, err = run_command("sx fetch-transaction "+tx_hash)
    if err != None:
        return err
    else:
        return out

def get_json_tx(raw_tx, tx_hash='unknown hash'):
    parsed_json_tx=None
    json_tx, err = run_command("sx showtx -j", raw_tx)
    if err != None:
        error(err)
    else:
        try:
            parsed_json_tx=simplejson.JSONDecoder().decode(json_tx)
        except simplejson.JSONDecodeError:
            error(str(json_tx)+' '+str(tx_hash))
    return parsed_json_tx

def get_tx(tx_hash):
    raw_tx=get_raw_tx(tx_hash)
    return get_json_tx(raw_tx, tx_hash)

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
    func_name='unknown'
    try:
        func_name=inspect.stack()[1][3]
    except IndexError:
        pass
    print '[E] '+func_name+': '+str(msg)
    exit(1)

def info(msg):
    func_name='unknown'
    try:
        func_name=inspect.stack()[1][3]
    except IndexError:
        pass
    print '[I] '+func_name+': '+str(msg)

def debug(debug_mode, msg):
    if debug_mode == True:
        func_name='unknown'
        try:
            func_name=inspect.stack()[1][3]
        except IndexError:
            pass
        print '[D] '+func_name+': '+str(msg)

# output_format is 'story' for long description of 'csv' for a short one
def output_per_tx(output_format, block, tx_hash, value, dacoins):
    if output_format == 'story':
        print 'block ' + str(block) + ' tx hash ' + str(tx_hash) + \
                ' value ' +str(value) + ' -> ' + str(dacoins) + ' dacoins'
    else:
        pass
# output_format is 'story' for long description of 'csv' for a short one
def output_per_address(output_format, address, dacoins):
    if output_format == 'story':
        print str(address) + ' got ' + dacoins + ' dacoin'
    else:
        print str(address) + ',' + dacoins

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
    parse_dict['padding']=data_script[36:42]
    return parse_dict


def parse_simple_basic(tx, tx_hash='unknown'):
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

        # validation of basic simple send transaction according to:
        # https://bitcointalk.org/index.php?topic=265488.msg3190175#msg3190175

        # all outputs has to be the same (except for change)
        if len(different_outputs_values) > 2:
            info('invalid mastercoin tx (different output values) '+tx_hash)
            return None

        # If there is an ambiguous sequence (i.e. 3,4,4), or perfect sequence (i.e. 3,4,5),
        # then the transaction is invalid!

        # if broken sequence (i.e. 3,4,8), then the odd-man-out is the change address

        # verify that all follow (n+1) mod 256 dataSequenceNum rule
        # verify not more than 255 data

        # currently support only the simple send (a single data packet)
        for s in seq_list:
            if (s+1)%256 == int(seq_list[(seq_list.index(s)+1)%len(seq_list)]):
                data=outputs_list_no_exodus[seq_list.index(s)]
                reference=outputs_list_no_exodus[(seq_list.index(s)+1)%len(seq_list)]

        to_address=reference['address']
        data_script=data['script'].split()[3].zfill(42)
        data_dict=parse_data_script(data_script)
        if len(data_dict) >= 6: # at least the basic 6 fields were parsed
            parse_dict=data_dict
            parse_dict['tx_hash']=tx_hash
            parse_dict['from_address']=from_address
            parse_dict['to_address']=to_address
            parse_dict['formatted_amount']=str(int(data_dict['amount'],16)/100000000.0)
            parse_dict['currency_str']=get_currency_type_from_dict(data_dict['currencyId'])
            parse_dict['tx_type_str']=get_transaction_type_from_dict(data_dict['transactionType'])
            parse_dict['tx_method_str']='basic'
            # FIXME: checksum?
            return parse_dict
    except KeyError, IndexError:
        info('invalid mastercoin tx '+tx_hash)

def parse_multisig_simple(tx):
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
        parse_dict['changeAddress'] = get_addr_from_key(change_address_pub)
        parse_dict['recipientAddress'] = b58encode(recipientHex.decode('hex_codec'))
        parse_dict['formatted_amount'] = str("{0:.8f}".format(int(data_dict['amount'],16)/100000000.0))
        parse_dict['currency_type_str'] = get_currency_type_from_dict(data_dict['currencyId'])
        parse_dict['transaction_type_str'] = get_transaction_type_from_dict(data_dict['transactionType'])
        parse_dict['transaction_method_str'] = 'multisig_simple'
        return parse_dict
    else:
        error('Bad parsing of data script '+data_script.encode('hex_codec'))
        return {}

def parse_multisig_long(tx):
    info('not implemented')

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
                different_outputs_values[output_value]+=1
            else:
                different_outputs_values[output_value]=1
        # take care if multiple 1EXoDus exist (for the case that someone sends msc
        # to 1EXoDus, or have 1EXoDus as change address)
        if len(outputs_to_exodus) != 1:
            error("not implemented tx with multiple 1EXoDus outputs: "+tx_hash)
        return (outputs_list_no_exodus, outputs_to_exodus, different_outputs_values)

def get_tx_method(tx, tx_hash='unknown'): # multisig_simple, multisig_long, multisig_invalid, basic
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
                        return 'multisig_long'
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

