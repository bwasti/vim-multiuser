" --------------------------------
" Add vim-multiuser to your path
" --------------------------------
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Functions
" --------------------------------
function! MultiUserServer(arg1)
python << endOfPython

from vim_multiuser import start_multiuser_server

port = int(vim.eval("a:arg1"))
if port == 0:
    port = 1337
print "Initializing multiuser server on port", port

start_multiuser_server(port)
#vim.eval("autocmd CursorMovedI * :call MultiUserCursorMoved()")

endOfPython
endfunction

function! MultiUserClient(arg1, arg2)
python << endOfPython

from vim_multiuser import start_multiuser_client

host = vim.eval("a:arg1").encode('ascii', 'ignore')
port = int(vim.eval("a:arg2"))

start_multiuser_client(host, port)
#vim.eval("autocmd CursorMovedI * :call MultiUserCursorMoved()")

endOfPython
endfunction

function! MultiUserAudioServer(arg1)
python << endOfPython

from vim_multiuser import start_multiuser_audio

port = int(vim.eval("a:arg1"))
if port == 0:
    port = 1337
print "Initializing multiuser server on port", port

start_multiuser_audio('0.0.0.0', port, 'server')
#vim.eval("autocmd CursorMovedI * :call MultiUserCursorMoved()")

endOfPython
endfunction

function! MultiUserAudioClient(arg1, arg2)
python << endOfPython

from vim_multiuser import start_multiuser_audio

host = vim.eval("a:arg1").encode('ascii', 'ignore')
port = int(vim.eval("a:arg2"))

start_multiuser_audio(host, port, 'client')
#vim.eval("autocmd CursorMovedI * :call MultiUserCursorMoved()")

endOfPython
endfunction

function! MultiUserCursorMoved()
python << endOfPython

from vim_multiuser import multiuser_client_send

multiuser_client_send()

endOfPython
endfunction

" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! MuS -nargs=1 call MultiUserServer(a:0)
command! MuC -nargs=2 call MultiUserClient(a:0, a:1)
autocmd CursorMovedI * :call MultiUserCursorMoved()
