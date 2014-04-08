import socket
import asyncore, asynchat
import sys, time
import vim
import json

"""
Globals
"""
session_list = {}

"""
Main Server Session Handler Class

"""
class MUSessionHandler(asynchat.async_chat):
    def __init__(self, sock, callback):
        asynchat.async_chat.__init__(self, sock=sock, map=session_list)
        
        self.set_terminator('\r\n')
        self.buffer = []
        self.callback = callback

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        data = ''.join(self.buffer)
        self.callback(data)
        for handler in session_list.itervalues():
            if hasattr(handler, 'push') and handler != self:
                handler.push(data + '\r\n')
        self.buffer = []

    def handle_close(self):
        asynchat.async_chat.handle_close(self)

"""
Main Server Class

"""
class MUServer(asyncore.dispatcher):
    def __init__(self, host, port, callback):
        asyncore.dispatcher.__init__(self, map=session_list)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(5)
        self.callback = callback

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = MUSessionHandler(sock, self.callback)
            
            # Initialize remote client with current buffer
            handler.push(json.dumps({
                'body':list(vim.current.buffer)
                })+'\r\n')

    def broadcast(self, msg):
        for handler in session_list.itervalues():
            if hasattr(handler, 'push'):
                handler.push(msg)

    def send_message(self, msg):
        self.broadcast(json.dumps(msg)+'\r\n')
        
"""
Main Client Class

"""
class MUClient(asynchat.async_chat):

    def __init__(self, host, port, callback):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

        self.set_terminator('\r\n')
        self.buffer = []
        self.callback = callback

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        data = ''.join(self.buffer)
        self.callback(data)
        self.buffer = []

    def send_message(self, msg):
        self.push(json.dumps(msg)+'\r\n')

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
