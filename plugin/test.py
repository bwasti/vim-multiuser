from vim_multiuser_server import *

server = MultiUserServer('0.0.0.0', 9999)
asyncore.loop()

