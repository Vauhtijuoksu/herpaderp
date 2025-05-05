import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os


class CORSRequestHandler(SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(CORSRequestHandler, self).end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        pass

parser = argparse.ArgumentParser(description="serveded")
parser.add_argument("--data-dir", help="data dir", default=None, type=str)
args = parser.parse_args()
os.chdir(args.data_dir + "/serve")

host = '0.0.0.0'
port = 8081

httpd = HTTPServer((host, port), CORSRequestHandler)
httpd.serve_forever()