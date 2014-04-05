" --------------------------------
" Add our plugin to the path
" --------------------------------
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Function(s)
" --------------------------------
function! MultiUser()
python << endOfPython

from vim_multiuser import start_multiuser

start_multiuser()

endOfPython
endfunction

" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! Multiuser call MultiUser()
