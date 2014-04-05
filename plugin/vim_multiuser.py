import vim
import threading
import time
from vim_multiuser_server import *

class MultiUserMain(object):
    def __init__(self):
        self.curr_buf = [""]
        self.thread = threading.Thread(target=self.main_loop, args = ())
        self.thread.daemon = True

    def run(self):
        self.thread.start()
        return

    def main_loop(self):
        while True:
            time.sleep (100.0 / 1000.0)
            self.curr_buf = [(i if i!="test" else "****") for i in list(vim.current.buffer)]
            vim.current.buffer[:] = self.curr_buf

def start_multiuser():
    multiuser = MultiUserMain()
    multiuser.run() 
