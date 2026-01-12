A simple script to install neovim from the offical AppImage.

# How do you run it?

curl --proto '=https' -sSfL https://github.com/geoffritter/neovim-install-appimage/releases/latest/download/neovim-install-appimage.sh | bash


# Why make this?

I wanted to make a bash script to do something once and was frustrated by there
being no 'verified' flatpak on flathub. AppImage also needs more love.


# Why not use "AM" Application Manger?

Go and use that if you wish. It's just a bunch of bash scripts and a 'database'
of tracked applications.


# Why is there also a python script?

I wanted to try out python scripting. If you want that version instead, download
it and run it. It has extra checks and validations that would otherwise be
annoying to do in bash.

python3 <(curl --proto '=https' -sSfL https://github.com/geoffritter/neovim-install-appimage/releases/latest/download/neovim-install-appimage.py)


# Why is there no .desktop file and icons?

I didn't want to bother extracting the files and adding them for a command line program.
