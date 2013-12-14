import urlparse
import os, sys
lib_path = os.path.abspath('..')
sys.path.append(lib_path)
from msc_utils_obelisk import *

http_status = '200 OK'

def response_with_error(start_response, environ, response_body):
    headers = [('Content-type', 'application/json')]
    start_response(http_status, headers)
    response='{"status":"'+response_body+'"}'
    return response

def verifybuyer_handler(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    http_status = 'invalid'
    response_status='OK' # 'OK', 'debug' or 'Non valid'
    if method == 'POST':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            request_body = environ['wsgi.input'].read(request_body_size)
        except (TypeError, ValueError):
            return response_with_error(start_response, environ, 'Bad environ in POST')
        try:
            response_dict=urlparse.parse_qs(request_body)
        except (TypeError, ValueError):
            return response_with_error(start_response, environ, 'Bad urlparse')
        try:
            buyers_list=response_dict['buyer']
        except KeyError:
            return response_with_error(start_response, environ, 'No buyer in dictionary')

        if len(buyers_list)!=1:
            return response_with_error(start_response, environ, 'No single buyer')
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

        headers = [('Content-type', 'application/json')]
        start_response(http_status, headers)
        response='{"status":"'+response_status+'", "debug":"'+debug+'"}'
        return response
    else:
        return response_with_error(start_response, environ, 'No POST')
