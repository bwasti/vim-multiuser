from vim_multiuser_server import *

client = MultiUserClient('localhost', 9999)

while True:
    to_send = raw_input("> ")
    client.send_message(to_send)
