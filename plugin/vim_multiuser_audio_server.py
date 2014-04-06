import socket

CHUNK = 1024
FORMAT = ""
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 4
WIDTH = 2

def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

class MultiUserAudioRecv(object):
    def __init__(self, host, port):
        if (module_exists("pyaudio")):
            import pyaudio
            FORMAT = pyaudio.paInt16
        else:
            self.failure = True
            return
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(WIDTH),
                                channels = CHANNELS,
                                rate = RATE,
                                output = True,
                                frames_per_buffer = CHUNK)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.run()
        
    def run(self):
        self.conn, self.addr = self.socket.accept()
        data = self.conn.recv(1024)
        while data != '':
            stream.write(data)
            self.data = self.conn.recv(1024)

class MultiUserAudioSend(object):
    def __init__(self, host, port):
        if (module_exists("pyaudio")):
            import pyaudio
            FORMAT = pyaudio.paInt16
        else:
            self.failure = True
            return
        self.p = pyaudio.PyAudio()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.stream = self.p.open(format=self.p.get_format_from_width(WIDTH),
                                channels = CHANNELS,
                                rate = RATE,
                                output = True,
                                frames_per_buffer = CHUNK)
         self.run()
    def run(self):
        while True:
            data = self.stream.read(CHUNK)
            socket.stream.sendall(data)
