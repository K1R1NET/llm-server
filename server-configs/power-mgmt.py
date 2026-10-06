from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse
import subprocess
import os

TOKEN = os.environ.get("POWER_TOKEN")

if not TOKEN:
    print("Error: variable POWER_TOKEN missing!")
    sys.exit(1)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        # Check token for all the commands below
        if query.get('token', [''])[0] != TOKEN:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden: Invalid or missing token\n")
            return

        # Server power off
        if parsed_path.path == '/shutdown':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Server goes to sleep. Bye!\n")
            os.system("shutdown -h now")
            return

        # webUI power on
        elif parsed_path.path == '/webui-on':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Starting Docker and Open WebUI...\n")
            # Starting in background: firstly Docker, then container itself
            subprocess.Popen("systemctl start docker && docker start open-webui", shell=True)
            return

        # webUI power off
        elif parsed_path.path == '/webui-off':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Stopping Open WebUI and killing Docker daemon...\n")
            # Starting in background: stopping container, Docker and containerd
            subprocess.Popen("docker stop open-webui && systemctl stop docker docker.socket containerd", shell=True)
            return
        
        # Wrong route
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Command Not Found\n")

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8081), RequestHandler).serve_forever()