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

```vim
autocmd myvimrc FileType python setlocal completeopt=menu,menuone,noinsert,noselect
```

This plugin will conflict with other completion plugins.
So you need to disable it.

Example (neocomplete)

```vim
" write after the above setting
autocmd myvimrc FileType python NeoCompleteLock
```

## Configuration

Configuration and error-check are not implemented yet.
Be careful.
