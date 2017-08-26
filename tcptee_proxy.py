# A tee for TCP, similar to `socal -v`.
#
#           | server
# client ---|
#           | stdout

import socket
from select import select
import sys
import logging
import socks

class TcpTee:

    def __init__(self, source_port, destination, proxy = None):
        self.destination = destination

        self.teesock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.teesock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.teesock.bind(('127.0.0.1', source_port))
        self.teesock.listen(200)
        socks.set_default_proxy(proxy['type'], proxy['server'], proxy['port'])
        self.use_proxy = True

        # Linked client/server sockets in both directions
        self.channel = {}

    def run(self):
        while 1:
            inputready, outputready, exceptready = select([self.teesock] + self.channel.keys(), [], [])
            for s in inputready:
                if s == self.teesock:
                    self.on_accept()
                    break

                data = s.recv(4096)
                if not data:
                    self.on_close(s)
                    break

                self.on_recv(s, data)

    def on_accept(self):
        clientsock, clientaddr = self.teesock.accept()
        if self.use_proxy:
            serversock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            serversock.connect(self.destination)
        except Exception:
            print 'Could not connect to server %s. Closing connection to client %s' % (self.destination, clientaddr)
            clientsock.close()
        else:
            print "%r has connected, connected to server %s" % (clientaddr, self.destination)
            self.channel[clientsock] = serversock
            self.channel[serversock] = clientsock

    def on_close(self, sock):
        print "%s has disconnected" % str(sock.getpeername())
        othersock = self.channel[sock]

        sock.close()
        othersock.close()

        del self.channel[sock]
        del self.channel[othersock]

    def on_recv(self, sock, data):
        #print data
        self.channel[sock].send(data)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("listen_port", help="The port this process will listen on.", type=int)
    parser.add_argument("server_host", help="The remote host to connect to.")
    parser.add_argument("server_port", help="The remote port to connect to.", type=int)
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    proxy = {
        "type": socks.SOCKS5,
        "server": "127.0.0.1",
        "port": 8000
    }
    tee = TcpTee(int(args.listen_port), (args.server_host, int(args.server_port)), proxy)
    try:
        tee.run()
    except KeyboardInterrupt:
        logging.info("Ctrl C - Good Bye")
        sys.exit(1)