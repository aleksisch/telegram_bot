from http.server import HTTPServer, CGIHTTPRequestHandler, SimpleHTTPRequestHandler
from constants import FOLDER_TO_SONG


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FOLDER_TO_SONG, **kwargs)


def start_server():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()
