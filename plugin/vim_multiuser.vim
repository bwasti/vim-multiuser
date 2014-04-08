" --------------------------------
" Add vim-multiuser to your path
" --------------------------------
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Functions
" --------------------------------

function! SetupMovementDetection()
autocmd CursorMovedI * :call MultiUserCursorMoved()
autocmd CursorMoved * :call MultiUserCursorMoved()
endfunction

function! MultiUserServer(arg1)
hi CursorHighlight ctermbg=DarkBlue ctermfg=White guibg=DarkBlue guifg=White gui=bold term=bold cterm=bold
:call SetupMovementDetection()
python << EOF

from vim_multiuser import start_multiuser_server

port = int(vim.eval("a:arg1"))
print "Initializing multiuser server on port", port

start_multiuser_server(port)

EOF
endfunction

function! MultiUserClient(arg1, arg2)
hi CursorHighlight ctermbg=DarkBlue ctermfg=White guibg=DarkBlue guifg=White gui=bold term=bold cterm=bold
:call SetupMovementDetection()
python << EOF

from vim_multiuser import start_multiuser_client

host = vim.eval("a:arg1").encode('ascii', 'ignore')
port = int(vim.eval("a:arg2"))
print "Connecting to host %s on port %s" %(host, str(port))

start_multiuser_client(host, port)

EOF
endfunction

function! MultiUserCursorMoved()
python << EOF

from vim_multiuser import multiuser_client_send

multiuser_client_send()

EOF
endfunction

" --------------------------------
"  TODO --> Expose our commands to the user without :call
" --------------------------------
