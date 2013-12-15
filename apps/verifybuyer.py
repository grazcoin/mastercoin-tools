import urlparse
import os, sys
lib_path = os.path.abspath('..')
sys.path.append(lib_path)
from msc_utils_obelisk import *
from msc_apps import *

def verifybuyer_response(response_dict):
    try:
        buyers_list=response_dict['buyer']
    except KeyError:
        return (None, 'No buyer in dictionary')
        
    if len(buyers_list)!=1:
        return response(None, 'No single buyer')
    buyer=buyers_list[0]
    
    # now verify
    l=len(buyer)
    if l == 66: # probably pubkey
        if is_pubkey_valid(buyer):
            debug='valid pubkey'
            response_status='OK'
        else:
            debug='invalid pubkey'
            response_status='invalid pubkey'
    else:   
        if verify_bcaddress(buyer) == None:
            debug='invalid address'
            response_status='invalid address'
        else:
            buyer_pubkey=get_pubkey(buyer)
            if is_pubkey_valid(buyer_pubkey):
                debug='valid address'
                response_status='OK'
            else:
                debug='missing pubkey'
                response_status='missing pubkey'
    response='{"status":"'+response_status+'", "debug":"'+debug+'"}'
    return (response, None)

def verifybuyer_handler(environ, start_response):
    return general_handler(environ, start_response, verifybuyer_response)
