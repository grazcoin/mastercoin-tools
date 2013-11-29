def verifybuyer_handler(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    return b'{"status":"OK"}'
