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

### Set root

This plugin searches `setup.py` upwards from the current file, to find project root.
If you want to use another file name, for example `.gitignore`, add the following setting.

```vim
let g:asyncjedi_root_filename = '.gitignore'
```

### Disable additional information

Jedi sometimes takes too long time to get docstring/descriptions.
If you encounter a performance issue, the following setting may help.

```vim
let g:asyncjedi_no_detail = 1
```

#### Default

![asyncjedi1.png](https://raw.githubusercontent.com/wiki/miyakogi/asyncjedi/asyncjedi1.png)

#### With no-detail option

![asyncjedi2.png](https://raw.githubusercontent.com/wiki/miyakogi/asyncjedi/asyncjedi2.png)
