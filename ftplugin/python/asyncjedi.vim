if get(b:, 'loaded_asyncjedi')
  finish
endif

if !asyncjedi#is_running()
  call asyncjedi#start_server()
endif

inoremap <buffer> <C-x><C-o> <C-R>=asyncjedi#complete()<CR>
autocmd TextChangedI,InsertEnter <buffer> call asyncjedi#complete()
if !exists(':AsyncJediClear')
  command! AsyncJediClear call asyncjedi#clear_cache()
endif

let b:loaded_asyncjedi = 1
