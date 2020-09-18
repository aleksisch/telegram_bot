from http.server import HTTPServer, CGIHTTPRequestHandler


def start_server():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, CGIHTTPRequestHandler)
    httpd.serve_forever()
