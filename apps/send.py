import urlparse
import os, sys
lib_path = os.path.abspath('..')
sys.path.append(lib_path)
from msc_utils_parsing import *
from msc_apps import *
import random

def send_form_response(response_dict):
    expected_fields=['from_address', 'to_address', 'amount', 'currency']
    for field in expected_fields:
        if not response_dict.has_key(field):
            return (None, 'No field '+field+' in response dict '+str(response_dict))
        if len(response_dict[field]) != 1:
            return (None, 'Multiple values for field '+field)
            
    from_addr=response_dict['from_address'][0]
    to_addr=response_dict['to_address'][0]
    amount=response_dict['amount'][0]
    currency=response_dict['currency'][0]
    if currency=='MSC':
        currency_id=1
    if currency=='TMSC':
        currency_id=2

    pubkey='unknown'
    tx_to_sign_dict='unknown'
    l=len(from_addr)
    if l == 66: # probably pubkey
        if is_pubkey_valid(from_addr):
            pubkey=from_addr
            response_status='OK'
        else:
            response_status='invalid pubkey'
    else:   
        if verify_bcaddress(from_addr) == None:
            response_status='invalid address'
        else:
            from_pubkey=get_pubkey(from_addr)
            if not is_pubkey_valid(from_pubkey):
                response_status='missing pubkey'
            else:
                pubkey=from_pubkey
                response_status='OK'
                tx_to_sign_dict=prepare_tx_for_signing(from_addr, to_addr, currency_id, amount)

    response='{"status":"'+response_status+'", "transaction":"'+tx_to_sign_dict['transaction']+'", "sourceScript":"'+tx_to_sign_dict['sourceScript']+'"}'
    return (response, None)


def prepare_tx_for_signing(from_address, to_address, currency_id, btc_amount, btc_fee=0.0005):

    # create multisig tx
  
    formatted_currency_id='{:08x}'.format(currency_id)
    amount=to_satoshi(btc_amount)
    fee=to_satoshi(btc_fee)

    tx_type=0 # only simple send is supported

    # check if address or pubkey was given as from address
    if from_address.startswith('0'): # a pubkey was given
        from_address_pub=from_address
        from_address=get_addr_from_key(from_address)
    else: # address was given
        from_address_pub=addrPub=get_pubkey(from_address)
        from_address_pub=from_address_pub.strip()

    # set change address to from address
    change_address_pub=from_address_pub
    changeAddress=from_address

    # get utxo required for the tx

    required_value=4*dust_limit
    dataSequenceNum=1

    dataHex = '{:02x}'.format(0) + '{:02x}'.format(dataSequenceNum) + \
            '{:08x}'.format(tx_type) + '{:08x}'.format(currency_id) + \
            '{:016x}'.format(amount) + '{:06x}'.format(0)

    dataBytes = dataHex.decode('hex_codec')
    dataAddress = hash_160_to_bc_address(dataBytes[1:21])

    utxo_all=get_utxo(from_address, required_value+fee)
    utxo_split=utxo_all.split()
    inputs_number=len(utxo_split)/12
    inputs=[]
    inputs_total_value=0

    if inputs_number < 1:
        error('zero inputs')
    for i in range(inputs_number):
        inputs.append(utxo_split[i*12+3])
        try:
            inputs_total_value += int(utxo_split[i*12+7])
        except ValueError:
            error('error parsing value from '+utxo_split[i*12+7])

    inputs_outputs='/dev/stdout'
    for i in inputs:
        inputs_outputs+=' -i '+i

    # simple send - multisig
    # dust to exodus
    # dust to to_address
    # double dust to rawscript "1 [ change_address_pub ] [ dataHex_obfuscated ] 2 checkmultisig"
    # change to change
    change_value=inputs_total_value-4*dust_limit-fee
    change_address_compressed_pub=get_compressed_pubkey_format(get_pubkey(changeAddress))
    obfus_str=get_sha256(from_address)[:62]
    padded_dataHex=dataHex[2:]+''.zfill(len(change_address_compressed_pub)-len(dataHex))[2:]
    dataHex_obfuscated=get_string_xor(padded_dataHex,obfus_str).zfill(62)
    random_byte=hex(random.randrange(0,255)).strip('0x').zfill(2)
    hacked_dataHex_obfuscated='02'+dataHex_obfuscated+random_byte
    info('plain dataHex: --'+padded_dataHex+'--')
    info('obfus dataHex: '+hacked_dataHex_obfuscated)
    valid_dataHex_obfuscated=get_nearby_valid_pubkey(hacked_dataHex_obfuscated)
    info('valid dataHex: '+valid_dataHex_obfuscated)
    script_str='1 [ '+change_address_pub+' ] [ '+valid_dataHex_obfuscated+' ] 2 checkmultisig'
    info('change address is '+changeAddress)
    info('too_address is '+to_address)
    info('total inputs value is '+str(inputs_total_value))
    info('fee is '+str(fee))
    info('dust limit is '+str(dust_limit))
    info('BIP11 script is '+script_str)
    dataScript=rawscript(script_str)
    change_value=inputs_total_value-4*dust_limit-fee
    # FIXME: handle the case of change smaller than dust limit.
    if change_value < 0:
        error ('negative change value')
    inputs_outputs+=' -o '+exodus_address+':'+str(dust_limit) + \
                    ' -o '+to_address+':'+str(dust_limit) + \
                    ' -o '+dataScript+':'+str(2*dust_limit)
    if change_value >= dust_limit:
        inputs_outputs+=' -o '+changeAddress+':'+str(change_value)
    else:
        # under dust limit leave all remaining as fees
        pass

    tx=mktx(inputs_outputs)
    info('inputs_outputs are '+inputs_outputs)
    info('parsed tx is '+str(get_json_tx(tx)))

    hash160=bc_address_to_hash_160(from_address).encode('hex_codec')
    prevout_script='OP_DUP OP_HASH160 ' + hash160 + ' OP_EQUALVERIFY OP_CHECKSIG'

    # tx, inputs
    return_dict={'transaction':tx, 'sourceScript':prevout_script}
    return return_dict


def send_handler(environ, start_response):
    return general_handler(environ, start_response, send_form_response)

