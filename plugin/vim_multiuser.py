import vim
import threading
import time, random
from vim_multiuser_server import *
from vim_multiuser_audio_server import *
  
old_buffer = []
emitter = None
connection_type = ""

class MultiUserAudioMain(object):
    def __init__(self, connection_type, host, port):
        self.connection_type = connection_type
        self.host = host
        self.port = port
        self.spawn_audio_threads()
    def spawn_audio_threads(self):
        self.audio_receiver_thread = threading.Thread(target=self.audio_receiver, args = ())
        self.audio_sender_thread = threading.Thread(target=self.audio_sender, args = ())

        self.audio_receiver_thread.daemon = True
        self.audio_sender_thread.daemon = True
        self.audio_receiver_thread.start()
        self.audio_sender_thread.start()

    def audio_receiver(self):
        if self.connection_type == 'client':
            self.audio_receiver = MultiUserAudioRecv('0.0.0.0', self.port+1)
        else:
            self.audio_receiver = MultiUserAudioRecv(self.host, self.port)

    def audio_sender(self):
        if self.connection_type == 'client':
            self.audio_sender = MultiUserAudioSend(self.host, self.port)
        else:
            self.audio_sender = MultiUserAudioSend(self.host, self.port+1)
    
    
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


def start_multiuser_server(host, port):
    multiuser = MultiUserMain('server', host, port)
    multiuser.run() 

def start_multiuser_client(host, port):
    multiuser = MultiUserMain('client', host, port)
    multiuser.run()

def start_multiuser_emitter(host, port, conn_type):
    global emitter
    global connection_type
    connection_type = conn_type
    emitter = MultiUserClientSender(host, port, conn_type)

def start_multiuser_audio(host, port, connection_type):
    audio = MultiUserAudioMain(connection_type, host, port)

def multiuser_client_send():
    global old_buffer
    if emitter == None: return
    current_buffer = list(vim.current.buffer)
    buffer_length = min(len(current_buffer), len(old_buffer))
    to_send = dict()
    to_send['timestamp'] = str(time.time()) + str(random.randint(0, 10000))
    equal_length = len(current_buffer) == len(old_buffer)
    deleting = len(current_buffer) + 1 == len(old_buffer)
    inserting = len(current_buffer) == len(old_buffer) + 1
    row,col = vim.current.window.cursor
    if row-1 < len(old_buffer) and current_buffer[row-1] != old_buffer[row-1] and equal_length:
        to_send['line'] = current_buffer[row-1]
        to_send['line_num'] = row-1
    elif not(equal_length):
        # we are deleting
        if (inserting):
            to_send['line'] = current_buffer[row-1]
            to_send['insert'] = row-1
        # we are deleting
        elif (deleting):
            to_send['delete'] = row-1
    old_buffer = current_buffer
    if ('line' in to_send or 'delete' in to_send):
        emitter.send_message(to_send)

