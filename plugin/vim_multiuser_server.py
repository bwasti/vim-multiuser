import socket
import asyncore, asynchat
import sys
#import vim

sessions = []

class MultiUserSession(asynchat.async_chat):
    def __init__(self, sock, server):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.ibuffer = []
        self.obuffer = ""
        self.set_terminator("\r\n\r\n")
    
    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer.append(data)
        self.server.broadcast(data)

    def found_terminator(self):
        self.ibuffer = []
        self.handle_request()

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        #call disconnect method
        
class MultiUserServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.server = self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))
        self.listen(5)
        print "initialized"

    def broadcast(self, data):
        print "broadcasting"
        global sessions
        if not sessions: return
        for i in sessions:
            i.push(data)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            session = MultiUserSession(sock, self)
            global sessions
            sessions.append(session)

class MultiUserClient(asyncore.dispatcher_with_send):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def send_message(self, message):
        self.out_buffer = message
        self.initiate_send()

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(8192)
        print data








