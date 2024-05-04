from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from urllib.parse import unquote

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'returnurl' in query_params:
            returnUrl = unquote(query_params['returnurl'][0])
            self.send_response(302)
            self.send_header('Location', returnUrl)
            self.end_headers()
            return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b'Error: returnurl parameter not found in the request.')

def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
