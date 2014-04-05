import vim
import threading
import time
from vim_multiuser_server import *

old_buffer = []
emitter = None

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
        start_multiuser_emitter(self.host, self.port)
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

def start_multiuser_emitter(host, port):
    global emitter
    emitter = MultiUserClientSender(host, port)

def multiuser_client_send():
    global old_buffer
    if emitter == None: return
    current_buffer = list(vim.current.buffer)
    for i in xrange(min(len(current_buffer), len(old_buffer))):
        if current_buffer[i] != old_buffer[i] and (emitter != None): 
            #print "Before"
            emitter.send_message({'line':current_buffer[i], 'line_num':i})
            #print "After"
    old_buffer = current_buffer
