import BaseHTTPServer, SimpleHTTPServer
import ssl
import patch_hosts
import threading

BLOG_URL = "README.md"

class ConfigHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.strip() == "/sync.conf":
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
            print "Processed request from Sync. Server shutting down..."
            assassin = threading.Thread(target=self.server.shutdown)
            assassin.daemon = True
            assassin.start()
        else:
            self.send_response(404, 'Not Found')
            self.end_headers()

def main():
    print "Please refer to %s for detailed instructions."  % BLOG_URL

    # Step 1
    #print "\r\nStep 1: patch hosts file (Admin required)...",
    if not patch_hosts.sync_patch_hosts(): return False
    #print "Done"

    # Step 2
    #print "\r\nStep 2: start fake config.resilio.com server..."
    httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 443), ConfigHandler)
    httpd.socket = ssl.wrap_socket (httpd.socket, keyfile='./do_not_trust.key', certfile='./do_not_trust.crt', server_side=True)
    print "Fake server started. Now, please restart Sync."
    print "After Sync has requested the config file, this program should go on automatically."
    print "If this program blocks here, please refer to %s" % BLOG_URL
    httpd.serve_forever()

    # Step 3
    #print "\r\nStep 3: restore hosts file (Admin required)...",
    if not patch_hosts.sync_unpatch_hosts(): return False
    #print "Done"

    return True

if __name__ == '__main__':
    if main():
        print "\r\nAll done. Sync should have updated the tracker/relay cache."
        print "Press Enter to exit."
    else:
        print "Error and abort."
    raw_input()
