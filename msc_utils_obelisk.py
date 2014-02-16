#!/usr/bin/python
import simplejson
import os
import msc_globals
from msc_utils_bitcoin import *

MAX_COMMAND_TRIES=3

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
        info(err)
        return (-1, -1)
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

def get_value_from_output(tx_and_number):
    try:
        txid=tx_and_number.split(':')[0]
        number=int(tx_and_number.split(':')[1])
    except IndexError:
        return None
    rawtx=get_raw_tx(txid)
    json_tx=get_json_tx(rawtx)
    if json_tx == None:
        error('json_tx is None')
    try:
        all_outputs=json_tx['outputs']
    except TypeError: # obelisk can give None
        error('bad outputs parsing on: '+json_tx)
    output=all_outputs[number]
    return output['value']

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

def get_balance(addrs):
    out, err = run_command("sx balance -j "+addrs)
    if err != None:
        return err
    else:
        try:
            parsed_json_balance=simplejson.JSONDecoder().decode(out)
        except simplejson.JSONDecodeError:
            error('error parsing balance json of '+addrs)
        return parsed_json_balance

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
