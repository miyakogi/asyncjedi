# AsyncJedi

Asynchronous Jedi auto-completion plugin for vim, using job and channel feature

## !!!CAUTION!!!

**!!! THIS PLUGIN IS HIGHLY EXPERIMENTAL AND UNSTABLE !!!**

## Features

- Asynchronous, non-blocking auto-completion
- Fast startup
- Fuzzy completion

Lots of other jedi's features (goto, rename, usage, and so on) are not implemented.

## Usage

**Extremely** recommended to add `noinsert` and `noselect` options to `'completeopt'`.

```vim
autocmd myvimrc FileType python setlocal completeopt+=noinsert,noselect
```

This plugin will conflict with other completion plugins.
So you need to disable it.

Example (neocomplete)

```vim
" write after the above setting
autocmd myvimrc FileType python NeoCompleteLock
```

## Configuration

This plugin searches `setup.py` upwards from the current editing file, to find project root.
If you want to use another file name, for example `.gitignore`, add the following setting.

```vim
let g:asyncjedi_root_filename = '.gitignore'
```
