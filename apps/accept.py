import urlparse
import os, sys
lib_path = os.path.abspath('..')
sys.path.append(lib_path)
from msc_utils_obelisk import *
from msc_apps import *

def accept_response(response_dict):
    expected_fields=['buyer', 'amount', 'tx_hash']
    for field in expected_fields:
        if not response_dict.has_key(field):
            return (None, 'No field '+field+' in response dict')
        if len(response_dict[field]) != 1:
            return (None, 'Multiple values for field '+field)
            
    buyer=response_dict['buyer'][0]
    amount=response_dict['amount'][0]
    tx_hash=response_dict['tx_hash'][0]
   
    pubkey='unknown' 
    l=len(buyer)
    if l == 66: # probably pubkey
        if is_pubkey_valid(buyer):
            pubkey=buyer
            response_status='OK'
        else:
            response_status='invalid pubkey'
    else:   
        if is_valid_bitcoin_address(buyer) == None:
            response_status='invalid address'
        else:
            buyer_pubkey=get_pubkey(buyer)
            if is_pubkey_valid(buyer_pubkey):
                pubkey=buyer_pubkey
                response_status='OK'
            else:
                response_status='missing pubkey'
    response='{"status":"'+response_status+'", "pubkey":"'+pubkey+'"}'
    return (response, None)

def accept_handler(environ, start_response):
    return general_handler(environ, start_response, accept_response)
