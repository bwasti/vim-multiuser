import vim
import threading
from vim_multiuser_server import *

"""
Globals
"""
MUConnection = None
old_buffer = []
old_tick = 0

"""
Set up functions (called directly from vim_multiuser.vim)
"""
def start_multiuser_server(port):
    global MUConnection
    MUConnection = MUServer('localhost', port)
    comm = threading.Thread(target=asyncore.loop,kwargs={'map':session_list})
    comm.daemon = True
    comm.start()

def start_multiuser_client(host, port):
    global MUConnection
    MUConnection = MUClient(host, port)
    comm = threading.Thread(target=asyncore.loop)
    comm.daemon = True
    comm.start()

"""
multiuser_client_send:

    This function determines what has changed in the file
    and then sends that data.

    Called on all cursor movement.
    
TODO:
    - Call on all key inputs
    - Better determine what has changed
    
"""
def multiuser_client_send():
    global old_buffer
    global MUConnection
    global old_tick
    
    # Check if there are changes
    new_tick = int(vim.eval("b:changedtick"))
    if old_tick != new_tick:
        old_tick = new_tick
    else:
        return
    
    # Get the current buffer
    current_buffer = list(vim.current.buffer)
    
    # Bools for quick checks
    equal_length = len(current_buffer) == len(old_buffer)
    deleting = len(current_buffer) + 1 == len(old_buffer)
    inserting = not equal_length and not deleting
    
    # Get the cursor position
    row,col = vim.current.window.cursor

    # Changes, but no insert or delete
    if (equal_length
      and current_buffer[row-1] != old_buffer[row-1]
      and row-1 < len(old_buffer)):
        line = current_buffer[row-1]
        line_num = row-1
        update_line(line, line_num)
        
        
    # Maybe insert, maybe delete
    elif not(equal_length):
        
        # we are inserting
        if (inserting):
            line = current_buffer[row-1]
            line_num = row-1
            prev_line = current_buffer[row-2]
            insert_line(line, prev_line, line_num)
            
        # we are deleting
        elif (deleting):
            prev_line = current_buffer[row-1]
            delete_line(prev_line, row)

    # Store the buffer
    old_buffer = current_buffer

"""
Utility functions for creating messages to send
"""

def insert_line(line, prev_line, line_num):
    to_send = dict()
    to_send['line'] = line
    to_send['insert'] = line_num
    MUConnection.send_message(to_send)
    if (line_num > 0):
        update_line(prev_line, line_num-1)

def delete_line(prev_line, line_num):
    to_send = dict()
    to_send['delete'] = line_num
    MUConnection.send_message(to_send)
    if (line_num > 0):
        update_line(prev_line, line_num-1)
    
def update_line(line, line_num):
    to_send = dict()
    to_send['line'] = line
    to_send['line_num'] = line_num
    MUConnection.send_message(to_send)