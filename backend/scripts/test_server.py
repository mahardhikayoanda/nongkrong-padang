from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'status': 'ok', 'message': 'Diagnostic Server Running'}
        self.wfile.write(json.dumps(response).encode())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print("Starting diagnostic server on port 8000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
