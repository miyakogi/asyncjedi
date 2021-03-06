let s:pyscript = expand('<sfile>:p:h:h') . '/server.py'
let s:handlers = []

function! asyncjedi#set_root(fname) abort
  let file = findfile(a:fname, escape(expand('<afile>:p:h'), ' ') . ';')
  if l:file != ''
    let b:asyncjedi_root_dir = substitute(l:file, '/setup.py$', '', 'g' )
  endif
endfunction

function! asyncjedi#is_running() abort
  if exists('s:port')
    return v:true
  else
    return v:false
  endif
endfunction

function! asyncjedi#complete_cb(ch, msg) abort
  call ch_close(a:ch)
  if mode() ==# 'i' && expand('%:p') ==# a:msg[2]
    call complete(a:msg[0], a:msg[1])
  endif
  let ind = index(s:handlers, a:ch)
  if ind >= 0
    call remove(s:handlers, ind)
  endif
endfunction

function! s:complete() abort
  if asyncjedi#is_running()
    let ch = ch_open('localhost:' . s:port, {'mode': 'json', 'waittime': 3})
    let st = ch_status(ch)
    if st ==# 'open'
      let msg = {}
      let msg.line = line('.')
      let msg.col = col('.')
      let msg.text = getline(0, '$')
      let msg.path = expand('%:p')
      let msg.root = get(b:, 'asyncjedi_root_dir')
      call ch_sendexpr(ch, msg, {'callback': 'asyncjedi#complete_cb'})
      call s:ch_clear()
      let s:handlers = [ch]
    else
      echomsg 'channel error: ' . st
    endif
  endif
  return ''
endfunction

function! asyncjedi#complete() abort
  call s:complete()
  return ''
endfunction

function! asyncjedi#clear_cache() abort
  if asyncjedi#is_running()
    let ch = ch_open('localhost:' . s:port, {'mode': 'json'})
    let st = ch_status(ch)
    if st ==# 'open'
      let msg = {'clear_cache':1}
      call ch_sendexpr(ch, msg)
    else
      echomsg 'channel error: ' . st
    endif
  endif
  return ''
endfunction

function! s:ch_clear() abort
  for ch in s:handlers
    if ch_status(ch) ==# 'open'
      call ch_close(ch)
    endif
  endfor
endfunction

function! asyncjedi#server_started(ch, msg) abort
  if a:msg =~ '\m^\d\+$'
    let s:port = str2nr(a:msg)
  elseif a:msg == '' || a:msg ==# 'DETACH'
    return
  else
    echomsg 'AsyncJediServer message: ' . string(a:msg)
  endif
endfunction

function! asyncjedi#wrap_ce(s) abort
  return "\<C-e>" . a:s
endfunction

let s:closepum=' <C-r>=pumvisible()?asyncjedi#wrap_ce("'
function! s:map(s) abort
  let cmd = 'inoremap <buffer><silent> ' . a:s . s:closepum . a:s . '"):"' . a:s . '"<CR>'
  execute cmd
endfunction

function! asyncjedi#mapping() abort
  for k in split('abcdefghijklmnopqrstuvwxyz', '\zs')
    call s:map(k)
    call s:map(toupper(k))
  endfor
  for k in split('123456789', '\zs')
    call s:map(k)
  endfor
  call s:map('_')
  call s:map('@')
  call s:map('\<BS>')
  call s:map('\<C-h>')
endfunction

function! asyncjedi#start_server() abort
  let ch = ch_open('localhost:8891', {'waittime': 10})
  if ch_status(ch) ==# 'open'
    " for debug
    let s:port = 8891
    echomsg 'AsyncJedi: use debug server at localhost:8891'
    call ch_close(ch)
  else
    let cmd = ['python3', s:pyscript]
    if !get(g:, 'asyncjedi_no_detail')
      call add(cmd, '--include-detail')
    endif
    let s:server = job_start(cmd, {'callback': 'asyncjedi#server_started'})
  endif
endfunction
