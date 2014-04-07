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
parse_data:
    
    This function is responsible for all parsing of data
    and loading of data into the vim buffer.
    
TODO:
    
    - Cursor handling

"""
def parse_data(data):
    try:
        recv_data = json.loads(data)
        
        # Line update --> simply swap out line with new one
        if ('line_num' in recv_data and 'line' in recv_data):
            line_num = recv_data[u'line_num']
            line = recv_data[u'line'].encode('ascii', 'ignore')
            vim.current.buffer[line_num] = line
        
        # Full body update --> swap entire buffer
        elif ('body' in recv_data):
            vim_list = recv_data[u'body']
            vim.current.buffer[:] = (
                    [vim_list[i].encode('ascii', 'ignore') 
                        for i in xrange(len(vim_list))])
        
        # Insert new line --> insert line and shift everything else down
        # TODO: move cursor with it
        elif ('insert' in recv_data):
            line_num = recv_data[u'insert']
            line = recv_data[u'line'].encode('ascii', 'ignore')

            vim.current.buffer[line_num+1:] = vim.current.buffer[line_num:]
            if line_num >= len(vim.current.buffer):
                vim.current.buffer[line_num:] = [line]
            else:
                vim.current.buffer[line_num] = line
        
        # Delete line --> remove line
        # TODO: move cursor appropriately
        elif ('delete' in recv_data):
            line_num = recv_data[u'delete']
            del vim.current.buffer[line_num]

        vim.command(":redraw")
        
    # Bad data
    except ValueError, e:
        pass

"""
Main Server Session Handler Class

"""
class MUSessionHandler(asynchat.async_chat):
    def __init__(self, sock):
        asynchat.async_chat.__init__(self, sock=sock, map=session_list)

        self.set_terminator('\r\n')
        self.buffer = []

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        data = ''.join(self.buffer)
        parse_data(data)
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
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self, map=session_list)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = MUSessionHandler(sock)
            
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

    def __init__(self, host, port):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

        self.set_terminator('\r\n')
        self.buffer = []

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        data = ''.join(self.buffer)
        parse_data(data)
        self.buffer = []

    def send_message(self, msg):
        self.push(json.dumps(msg)+'\r\n')

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
