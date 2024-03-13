import base64
import http.server
import socketserver
import os

# Define the directory containing your index.html file
web_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(web_dir)

PORT = 8000

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    ''' Main class to present webpages and authentication. '''
    def do_HEAD(self):
        ''' Send header '''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        ''' Send 401 response for authentication '''
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Unauthorized', 'utf8'))
        elif self.headers.get('Authorization') == 'Basic ' + base64.b64encode(bytes('paco:paco', 'utf8')).decode('utf8'):
            http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Unauthorized', 'utf8'))

with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
    print(f"Serving 'index.html' at localhost:{PORT}")
    httpd.serve_forever()
