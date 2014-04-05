import socket
import asyncore, asynchat
import sys
import vim
import json

sessions = []

class MultiUserSession(asynchat.async_chat):
    def __init__(self, sock, server):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.ibuffer = []
        self.obuffer = ""
        self.vbuffer = []
        self.set_terminator("\r\n\r\n")
    
    def collect_incoming_data(self, data):
        self.ibuffer.append(data)
        self.server.broadcast(data)
        self.server.parse_data(data)

    def found_terminator(self):
        self.ibuffer = []
        self.handle_request()

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        
class MultiUserServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.server = self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))
        self.listen(5)

    def broadcast(self, data):
        global sessions
        if not sessions: return
        for i in sessions:
            i.push(data)

    def parse_data(self, data):
        try:
            recv_data = json.loads(data)
            line_num = recv_data[u'line_num']
            line = recv_data[u'line'].encode('ascii', 'ignore')
            vim_list = list(vim.current.buffer)
            vim.current.buffer[:] = [vim_list[i] if i!=line_num else line for i in xrange(len(vim_list))]
        except ValueError, e:
            pass
            vim.current.buffer[:] = [str(e), data]


    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            session = MultiUserSession(sock, self)
            global sessions
            sessions.append(session)

class MultiUserClientReader(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_close(self):
        self.close()

    def parse_data(data):
        recv_data = json.loads(data)
        line_num = recv_data[u'line_num']
        line = recv_data[u'line']
        vim.current.buffer[:] = [i if i!=line_num else line for i in list(vim.current.buffer)]

    def handle_read(self):
        data = self.recv(8192)
        vim.current.buffer[:] = [data]

class MultiUserClientSender(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host,port))
    
    def send_message(self, message):
        print "sending"
        self.connection.send(message)





