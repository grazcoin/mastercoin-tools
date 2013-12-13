import urlparse

def verifybuyer_handler(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    http_status = '200 OK'
    reposone_status='OK' # 'OK', 'debug' or 'Non valid'
    if method == 'POST':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            request_body = environ['wsgi.input'].read(request_body_size)
        except (TypeError, ValueError):
            request_body = "{}"
        try:
            response_body=str(urlparse.parse_qs(request_body))
        except:
            response_body = "error"
        headers = [('Content-type', 'application/json')]
        start_response(http_status, headers)
        response='{"status":"'+reposone_status+'", "response_body":"'+response_body+'"}'
        return response
    else:
        response_body = 'No POST'
        http_status = '200 OK'
        headers = [('Content-type', 'text/html'),
                    ('Content-Length', str(len(response_body)))]
        start_response(http_status, headers)
        return [response_body]
