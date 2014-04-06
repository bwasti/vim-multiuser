import vim
import threading
import time, random
from vim_multiuser_server import *

old_buffer = []
emitter = None
connection_type = ""

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
        start_multiuser_emitter(self.host, self.port, self.connection_type)
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

def start_multiuser_emitter(host, port, conn_type):
    global emitter
    global connection_type
    connection_type = conn_type
    emitter = MultiUserClientSender(host, port, conn_type)

def multiuser_client_send():
    global old_buffer
    if emitter == None: return
    current_buffer = list(vim.current.buffer)
    buffer_length = min(len(current_buffer), len(old_buffer))
    to_send = dict()
    to_send['timestamp'] = str(time.time()) + str(random.randint(0, 10000))
    for i in xrange(buffer_length):
        if current_buffer[i] != old_buffer[i] and (emitter != None): 
            """Check for entire line insertion."""
            if ((i != len(current_buffer)-1 and current_buffer[i+1:] == old_buffer[i:])
              and len(current_buffer) == (len(old_buffer)+1)):
                to_send['line'] = current_buffer[i]
                to_send['insert'] = i
                break
            elif (i == len(current_buffer)-1 and len(current_buffer) == len(old_buffer)+1):
                to_send['line'] = current_buffer[i]
                to_send['insert'] = i
            elif ((i != len(old_buffer)-1 and current_buffer[i:] == old_buffer[i+1:])
              and (len(current_buffer)+1) == len(old_buffer)):
                to_send['delete'] = i
                break
            else:
                to_send['line'] = current_buffer[i]
                to_send['line_num'] = i
                break
    
    old_buffer = current_buffer
    emitter.send_message(to_send)





