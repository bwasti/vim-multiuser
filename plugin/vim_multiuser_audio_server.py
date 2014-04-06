import socket
import time
import vim

CHUNK = 1024
FORMAT = ""
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 40
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
        self.host = '0.0.0.0'
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
        self.socket.bind((self.host, port))
        self.socket.listen(1)
        self.run()
        
    def run(self):
        self.conn, self.addr = self.socket.accept()
        data = self.conn.recv(4*CHUNK)
        while data != '':
            self.stream.write(data)
            data = self.conn.recv(1024)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.conn.close()

class MultiUserAudioSend(object):
    def __init__(self, host, port):
        if (module_exists("pyaudio")):
            import pyaudio
            FORMAT = pyaudio.paInt16
        else:
            self.failure = True
            return
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(WIDTH),
                                channels = CHANNELS,
                                rate = RATE,
                                input = True,
                                frames_per_buffer = CHUNK)
        self.attempt_connect()

    def attempt_connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.run()
        except Exception as e:
            time.sleep(1)
            self.attempt_connect()

    def run(self):
        while self.stream.is_active():
            data = self.stream.read(CHUNK)
            self.socket.sendall(data)

