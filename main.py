from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json
import os

HOST = 'localhost'
HTTP_PORT = 3000
SOCKET_PORT = 5000

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/':
            self.send_html_file('index.html')
        elif parsed_url.path == '/message':
            self.send_html_file('message.html')
        elif parsed_url.path == '/style.css':
            self.send_static_file('style.css', 'text/css')
        elif parsed_url.path == '/logo.png':
            self.send_static_file('logo.png', 'image/png')
        else:
            self.send_html_file('error.html', 404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)

        if self.path == '/message':
            username = parsed_data['username'][0] if 'username' in parsed_data else ''
            message = parsed_data['message'][0] if 'message' in parsed_data else ''
            if username and message:
                self.store_message(username, message)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Message sent successfully')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Error: Username and message are required')

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_static_file(self, filename, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def store_message(self, username, message):
        current_time = datetime.now().isoformat()
        data = {
            'username': username,
            'message': message
        }
        with open(os.path.join('storage', 'data.json'), 'a') as file:
            file.write(json.dumps({current_time: data}) + '\n')

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run_http_server():
    server_address = (HOST, HTTP_PORT)
    httpd = ThreadedHTTPServer(server_address, HttpHandler)
    print(f'Starting HTTP server on http://{HOST}:{HTTP_PORT}')
    httpd.serve_forever()


def run_socket_server():
    pass

if __name__ == '__main__':
    try:
        from threading import Thread
        http_server = Thread(target=run_http_server)
        http_server.start()

        socket_server = Thread(target=run_socket_server)
        socket_server.start()

        http_server.join()
        socket_server.join()

    except KeyboardInterrupt:
        print('Stopping servers...')

import socket

SOCKET_HOST = 'localhost'
SOCKET_PORT = 5000

def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((SOCKET_HOST, SOCKET_PORT))
        print(f'Starting Socket server on udp://{SOCKET_HOST}:{SOCKET_PORT}')

        while True:
            data, addr = sock.recvfrom(1024)
            if data:
                try:
                    message = json.loads(data.decode('utf-8'))
                    store_message_from_socket(message)
                except json.JSONDecodeError as e:
                    print(f'Error decoding JSON: {e}')

def store_message_from_socket(message):
    current_time = datetime.now().isoformat()
    data = {
        'username': message.get('username', ''),
        'message': message.get('message', '')
    }
    with open(os.path.join('storage', 'data.json'), 'a') as file:
        file.write(json.dumps({current_time: data}) + '\n')

if __name__ == '__main__':
    try:

        from threading import Thread
        http_server = Thread(target=run_http_server)
        http_server.start()

        socket_server = Thread(target=run_socket_server)
        socket_server.start()

        http_server.join()
        socket_server.join()

    except KeyboardInterrupt:
        print('Stopping servers...')
