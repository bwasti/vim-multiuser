import vim
import threading
from vim_multiuser_server import *
import random

"""
Globals
"""
MUConnection = None
old_buffer = []
old_tick = 0
cursors = {}
user_name = ""

"""
Set up functions (called directly from vim_multiuser.vim)
"""
def start_multiuser_server(port, name=""):
    global user_name
    if name != "":
        user_name = name
    else:
        user_name = "User"+str(random.randint(0,100000))
    global MUConnection
    MUConnection = MUServer('localhost', port, parse_data)
    comm = threading.Thread(target=asyncore.loop,kwargs={'map':session_list})
    comm.daemon = True
    comm.start()

def start_multiuser_client(host, port, name=""):
    global user_name
    if name != "":
        user_name = name
    else:
        user_name = "User"+str(random.randint(0,100000))
    global MUConnection
    MUConnection = MUClient(host, port, parse_data)
    comm = threading.Thread(target=asyncore.loop)
    comm.daemon = True
    comm.start()

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

        if ('user_name' in recv_data and 'cursor_row' in recv_data
            and 'cursor_col' in recv_data):
            if recv_data[u'user_name'] not in cursors:
                user_id = len(cursors)+6
            else:
                user_id = cursors[recv_data[u'user_name']][2]
                vim.command(':call matchdelete('+str(user_id)+')')

            # Update the cursor dict with row, col, color
            cursors[recv_data[u'user_name']] = (
                recv_data[u'cursor_row'],
                recv_data[u'cursor_col'],
                user_id)

            # Update collaborator cursor visually
            vim.command(':call matchadd(\'CursorHighlight\',\'\%'+
                str(recv_data[u'cursor_col'])+
                'v.\%'+str(recv_data[u'cursor_row'])+
                'l\', 1, '+str(user_id)+')')

        # Line update --> simply swap out line with new one
        elif ('line_num' in recv_data and 'line' in recv_data):
            line_num = recv_data[u'line_num']
            line = recv_data[u'line'].encode('ascii', 'ignore')
            vim.current.buffer[line_num] = line

        # Full body update --> swap entire buffer
        elif ('body' in recv_data):
            old_buffer = []
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
    
    # Send cursor data
    update_cursor(*vim.current.window.cursor)
            
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
    elif not equal_length and not old_buffer == []:
        
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
    
def update_cursor(row, col):
    global user_name
    to_send = dict()
    to_send['user_name'] = user_name
    to_send['cursor_row'] = row
    to_send['cursor_col'] = col
    MUConnection.send_message(to_send)
