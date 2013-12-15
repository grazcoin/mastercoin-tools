import urlparse
import os, sys
lib_path = os.path.abspath('..')
sys.path.append(lib_path)
from msc_utils_obelisk import *
from msc_apps import *

def send_form_response(response_dict):
    expected_fields=['from', 'to', 'amount', 'currency']
    for field in expected_fields:
        if not response_dict.has_key(field):
            return (None, 'No field '+field+' in response dict')
        if len(response_dict[field]) != 1:
            return (None, 'Multiple values for field '+field)
            
    from_addr=response_dict['from'][0]
    to_addr=response_dict['to'][0]
    amount=response_dict['amount'][0]
    currency=response_dict['currency'][0]
   
    pubkey='unknown'
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
            if is_pubkey_valid(from_pubkey):
                pubkey=from_pubkey
                response_status='OK'
            else:
                response_status='missing pubkey'
    response='{"status":"'+response_status+'", "pubkey":"'+pubkey+'"}'
    return (response, None)

def send_handler(environ, start_response):
    return general_handler(environ, start_response, send_form_response)
