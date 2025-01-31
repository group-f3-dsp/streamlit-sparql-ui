# this is deprecated and no longer in use

import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

class JSONHandler(SimpleHTTPRequestHandler):
    """
    A simple HTTP handler that serves JSON content from memory.
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(self.server.jsonld_data.encode())

class JSONLDServer:
    """
    A small wrapper around Python's HTTPServer to serve JSON-LD content.
    """
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start_server(self, jsonld_data: str):
        """
        Start the HTTP server in a separate thread.
        """
        def handler(*args):
            self._JSONHandler = JSONHandler
            self._JSONHandler.server = self.server
            self.server.jsonld_data = jsonld_data
            JSONHandler(*args)

        self.server = HTTPServer((self.host, self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop_server(self):
        """
        Stop the server if it's running.
        """
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.thread = None
