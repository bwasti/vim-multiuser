import vim
import threading
import time
from vim_multiuser_server import *

class MultiUserMain(object):
    def __init__(self, connection_type, host, port):
        self.curr_buf = [""]
        self.port = port
        self.host = host
        self.thread = threading.Thread(target=self.main_loop, args = ())
        self.thread.daemon = True
        self.connection_type = connection_type

    def run(self):
        self.thread.start()
        return

    def main_loop(self):
        if (self.connection_type == 'server'):
            self.server = MultiUserServer(self.host, self.port)
        else:
            self.client_reader = MultiUserClientReader(self.host, self.port)
        asyncore.loop()

def start_multiuser_server(port):
    multiuser = MultiUserMain('server', '0.0.0.0', port)
    multiuser.run() 

def start_multiuser_client(host, port):
    multiuser = MultiUserMain('client', host, port)
    multiuser.run()
