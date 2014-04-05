" --------------------------------
" Add our plugin to the path
" --------------------------------
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Function(s)
" --------------------------------
function! MultiUserServer(arg1)
python << endOfPython

from vim_multiuser import start_multiuser_server

port = int(vim.eval("a:arg1"))
if port == 0:
    port = 1337
print "Initializing on port", port

start_multiuser_server(port)

endOfPython
endfunction

function! MultiUserClient(arg1, arg2)
python << endOfPython

from vim_multiuser import start_multiuser_client

host = '0.0.0.0'#vim.eval("a:arg1")
port = 1337#vim.eval("a:arg2")

start_multiuser_client(host, port)

endOfPython
endfunction


" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! MuS -nargs=1 call MultiUserServer(a:0)
command! MuC -nargs=2 call MultiUserClient(a:0, a:1)
