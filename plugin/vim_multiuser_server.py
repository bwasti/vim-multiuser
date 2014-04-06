import socket
import asyncore, asynchat
import sys
import vim
import json

sessions = []
cursor = (1,0)
just_sent = ""

def parse_data(data):
    try:
        recv_data = json.loads(data)
        if ('timestamp' in recv_data):
            if (recv_data['timestamp'] == just_sent):
                return
        else:
            return
        if ('line_num' in recv_data and 'line' in recv_data):
            line_num = recv_data[u'line_num']
            line = recv_data[u'line'].encode('ascii', 'ignore')
            vim_list = list(vim.current.buffer)
            vim.current.buffer[:] = (
                    [elem if i!=line_num 
                        else line for i,elem in enumerate(vim_list)])
        elif ('body' in recv_data):
            vim_list = recv_data[u'body']
            vim.current.buffer[:] = (
                    [vim_list[i].encode('ascii', 'ignore') for i in xrange(len(vim_list))])
        elif ('insert' in recv_data):
            line_num = recv_data[u'insert']
            line = recv_data[u'line'].encode('ascii', 'ignore')
            vim_list = list(vim.current.buffer)
            vim_list.insert(line_num, line)
            vim.current.buffer[:] = vim_list 
        elif ('delete' in recv_data):
            line_num = recv_data[u'delete']
            vim_list = list(vim.current.buffer)
            if (line_num < len(vim_list)):
                vim_list.pop(line_num)
            vim.current.buffer[:] = vim_list
        global cursor
        vim.current.window.cursor = vim.current.window.cursor
        vim.command(":redraw")
    except ValueError, e:
        #vim.current.buffer[:] = [str(e), data]
        pass

class MultiUserSession(asynchat.async_chat):
    def __init__(self, sock, server, session_id):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.ibuffer = []
        self.obuffer = ""
        self.vbuffer = []
        self.set_terminator("\r\n\r\n")
        self.session_id = session_id
    
    def collect_incoming_data(self, data):
        self.ibuffer.append(data)
        self.server.broadcast(data, self.session_id)
        parse_data(data)

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
        self.session_id = 0

    def broadcast(self, data, session_id):
        global sessions
        if not sessions: return
        for i in sessions:
            if i.session_id != session_id:
                i.push(data)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            self.session_id += 1
            session = MultiUserSession(sock, self, self.session_id)
            global sessions
            session.push(json.dumps({'body':list(vim.current.buffer),'timestamp':'yeezus'}))
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

    def handle_read(self):
        data = self.recv(8192)
        parse_data(data)

class MultiUserClientSender(object):
    def __init__(self, host, port, connection_type):
        self.host = host
        self.port = port
        self.connection_type = connection_type
        if (connection_type == 'client'):
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((host,port))
    
    def send_message(self, message):
        global cursor
        cursor = vim.current.window.cursor
        if (self.connection_type == 'client'):
            self.connection.send(json.dumps(message))
            just_sent = message['timestamp']
        else:
            self.broadcast(message)

    def broadcast(self, message):
        global sessions
        if not sessions: return
        for i in sessions:
            i.push(json.dumps(message))





