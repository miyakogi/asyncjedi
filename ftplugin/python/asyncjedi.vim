if get(b:, 'loaded_asyncjedi')
  finish
endif

if !asyncjedi#is_running()
  call asyncjedi#start_server()
endif
call asyncjedi#set_root(get(g:, 'asyncjedi_root_filename', 'setup.py'))

inoremap <buffer> <C-x><C-o> <C-R>=asyncjedi#complete()<CR>
autocmd TextChangedI,InsertEnter <buffer> call asyncjedi#complete()
if get(g:, 'asyncjedi_override_completion')
  call asyncjedi#mapping()
endif

if !exists(':AsyncJediClear')
  command! AsyncJediClear call asyncjedi#clear_cache()
endif

let b:loaded_asyncjedi = 1
