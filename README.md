# vim-multiuser

## Installation

Use your plugin manager of choice.

- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/emgram769/vim-multiuser ~/.vim/bundle/vim-multiuser`
- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'https://github.com/emgram769/vim-multiuser'` to .vimrc
  - Run `:BundleInstall`
- [NeoBundle](https://github.com/Shougo/neobundle.vim)
  - Add `NeoBundle 'https://github.com/emgram769/vim-multiuser'` to .vimrc
  - Run `:NeoBundleInstall`
- [vim-plug](https://github.com/junegunn/vim-plug)
  - Add `Plug 'https://github.com/emgram769/vim-multiuser'` to .vimrc
  - Run `:PlugInstall`

## Usage

- Set up a server
  - `:call MultiUserServer(port)`
- Set up a client
  - `:call MultiUserClient(host, port)`
