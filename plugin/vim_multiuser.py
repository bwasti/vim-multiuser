import vim
import threading
from vim_multiuser_server import *
import random
import difflib

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
    MUConnection = MUServer('0.0.0.0', port, parse_data)
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

    - Refactor code for clarity

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

        # Full body update --> swap entire buffer
        elif ('body' in recv_data):
            vim_list = recv_data[u'body']
            vim.current.buffer[:] = (
                    [vim_list[i].encode('ascii', 'ignore') 
                        for i in xrange(len(vim_list))])

        elif ('type' in recv_data):
            head = vim.current.buffer[:recv_data['start']]
            tail = vim.current.buffer[recv_data['end']:]
            mid = [x.encode('ascii','ignore') for x in recv_data['new_section']]
            vim.current.buffer[:] = head + mid + tail

        # Buffer has been updated, save that fact
        global old_buffer
        old_buffer = list(vim.current.buffer)

        vim.command(":redraw")

    # Bad data
    except ValueError, e:
        pass


"""
multiuser_client_send:

    This function determines what has changed in the file
    and then sends that data.

    Called on all key presses.
    
"""
def multiuser_client_send():
    global old_buffer
    global MUConnection
    global old_tick
    
    if MUConnection == None:
        return
    
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
    
    run_diff(old_buffer, current_buffer)
    old_buffer = current_buffer
    return

"""
Utility functions for creating messages to send
"""

def run_diff(old, new):
    matcher = difflib.SequenceMatcher(None, old, new)
    for tag, old_start, old_end, new_start, new_end in reversed(matcher.get_opcodes()):
        if tag == 'delete':
            insert_range(old_start, old_end, [])
        if tag == 'insert':
            insert_range(old_start, old_end, new[new_start:new_end])
        if tag == 'replace':
            insert_range(old_start, old_end, new[new_start:new_end])

def insert_range(old_start, old_end, new_section):
    to_send = dict()
    to_send['type'] = "insert_range"
    to_send['start'] = old_start
    to_send['end'] = old_end
    to_send['new_section'] = new_section
    MUConnection.send_message(to_send)

def update_cursor(row, col):
    global user_name
    to_send = dict()
    to_send['type'] = "cursor"
    to_send['user_name'] = user_name
    to_send['cursor_row'] = row
    to_send['cursor_col'] = col
    MUConnection.send_message(to_send)
