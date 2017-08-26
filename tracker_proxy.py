import sys
import threading
import json
import logging
import socks
from tcptee_proxy import TcpTee

TCP_FORWARDS = [
    {"local_port": 4000, "remote_server": ("173.244.217.42",4000)},
    {"local_port": 4001, "remote_server": ("209.95.56.60",4000)},
    {"local_port": 3000, "remote_server": ("107.182.230.198",3000)},
    {"local_port": 3001, "remote_server": ("173.244.209.150",3000)},
]

class TCP_Proxy_Thread(threading.Thread):
    def __init__(self, source_port, destination, proxy = None):
        threading.Thread.__init__(self)
        self.tee = TcpTee(source_port, destination, proxy)

    def run(self):
        self.tee.run()

def main():
    conf = json.load(open("./proxy.conf"))
    if 'gfw_proxy' in conf:
        proxy = conf['gfw_proxy']
        if proxy['type'] == "socks5":
            proxy['type'] = socks.SOCKS5
        elif proxy['type'] == "socks4":
            proxy['type'] = socks.SOCKS4
        else:
            print "Only support SOCKS4/5 proxy."
            return

        print "Start TCP Proxies..."
        for f in TCP_FORWARDS:
            trd = TCP_Proxy_Thread(f['local_port'], f['remote_server'], proxy)
            trd.start()
    else:
        print "gfw_proxy not defined in proxy.conf"

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()
