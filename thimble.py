"""
  Thimble -- A tiny web framework in the spirit of Flask, but scaled down to run on microcontrollers.
"""

from socket import socket, getaddrinfo, AF_INET, SOCK_STREAM

class Thimble:
    def __init__(self, default_content_type='text/plain', req_buffer_size=1024):
        self.routes = {}  # Dictionary to map method and URL path combinations to functions
        self.default_content_type = default_content_type
        self.req_buffer_size = req_buffer_size
        self.server_name = 'Thimble (MicroPython)'


    # HTTP responses consist of a numeric code sent with a textual description, so here's a subset.
    http_status_text = {
        200: "200 OK",
        400: "400 Bad Request",
        404: "404 Not Found",
        500: "500 Internal Server Error"
    }


    # Generate an HTTP response status line based on code. Unknown codes result in a 500.
    # Returns a string similar to: HTTP/1.1 200 OK
    @staticmethod
    def http_response_status(status_code):
        if (status_code not in Thimble.http_status_text):
            status_code = 500
            
        return f'HTTP/1.1 {Thimble.http_status_text[status_code]}'


    # Given a query string, in the format key1=value1&key2=value2, return a dictionary of key/value pairs.
    @staticmethod
    def parse_query_string(query_string):
        query = {}
        query_params = query_string.split('&')
        for param in query_params:
            if (not '=' in param):  # Example: somebody sent ?on instead of ?state=on
                key=param
                query[key] = ''
            else:
                key, value = param.split('=')
                query[key] = value
                
        return query


    # Given a raw HTTP request, return a dictionary with individual elements broken out.
    # Takes a buffer containing the HTTP request sent from the client.
    # Returns a dictionary containing method, path, query, headers, body, etc. or None if parsing fails.
    @staticmethod
    def parse_http_request(req_buffer):
        req = {}
        req_buffer_lines = req_buffer.decode('utf8').split('\r\n')
        req['method'], target, req['http_version'] = req_buffer_lines[0].split(' ', 2)  # Example: GET /route/path HTTP/1.1
        if (not '?' in target):
            req['path'] = target
        else:  # target can have a query component, so /route/path could be something like /route/path?state=on&timeout=30
            req['path'], query_string = target.split('?', 1)
            req['query'] = Thimble.parse_query_string(query_string)

        req['headers'] = {}
        for i in range(1, len(req_buffer_lines) - 1):
            if (req_buffer_lines[i] == ''):  # Blank line signifies the end of headers.
                break
            else:
                name, value = req_buffer_lines[i].split(':', 1)
                req['headers'][name.strip()] = value.strip()

        req['body'] = req_buffer_lines[len(req_buffer_lines) - 1]  # Last line is the body (or blank if no body.)
        
        return req


    # Given a path and list of zero or more HTTP methods, add the decorated function to the route table. 
    def route(self, url_path, methods=['GET']):
        def add_route(func):
            for method in methods:
                self.routes[method.upper() + url_path] = func  # Methods are uppercase (see RFC 9110.)
        return add_route


    # Given the method and path of an HTTP request, look up the function in the route table and execute it.
    # Returns (body, status_code) tuple. Example: ("Hello!", 200) or ("", 404) if no route or ("", 500) on error.
    def call_route_function(self, req):
        route_key = req['method'] + req['path']
        body = ''
        status_code = 0

        if (not route_key in self.routes or not callable(self.routes[route_key])):  # No function in the route table?
            status_code = 404
        else:
            try:
                result = self.routes[route_key](req)  # Execute function in routing table, passing request parameters.
                if (isinstance(result, tuple)):  # User-defined functions can respond with a body, status code tuple or just a body.
                    body = res[0]
                    status_code = res[1]
                else:
                    body = result
                    status_code = 200  # Assume 200 OK when it's just a body in the response.
            except:
                status_code = 500

        if (not isinstance(body, str)):
            body = str(body)
                
        return body, status_code


    # Start listening for connections.
    def run(self, host='0.0.0.0', port=80, debug=False):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(getaddrinfo(host, port)[0][-1])
        sock.listen()
        print(f'Listening on {host}:{port}')

        while (True):
            req = None
            body = None
            status_code = None
            res = []

            conn, client = sock.accept()
            if (debug): print(f'Connection from: {client}')
            try:
                req_buffer = conn.recv(self.req_buffer_size)
                req = Thimble.parse_http_request(req_buffer)
            except:
                if (debug): print(f'Unable to parse HTTP request: {req_buffer}\n')
                body = 'Invalid Request'
                status_code = 400
            else:
                if (debug): print(f'Request: {req}')
                if (debug): print(f'Looking up function for route: {req['method']} {req['path']}')
                body, status_code = self.call_route_function(req)
                res.append(Thimble.http_response_status(status_code))
                res.append(f'Content-Length: {len(body)}')
                res.append(f'Content-Type: {self.default_content_type}')
                res.append(f'Server: {self.server_name}')
                res.append('Connection: close')
                res.append('')
                res.append(f'{body}')
                if (debug): print('\r\n'.join(res))
                conn.send('\r\n'.join(res))
                conn.close()

