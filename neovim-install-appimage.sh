#!/bin/env bash
# Download the official app image for neovim and set it up for use.

TARGETDIR=${1:-/opt/nvim}
DOWNLOADDIR="$HOME/Downloads"

SCRIPTPATH="$(readlink -f "$0")"
URL="https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.appimage"
APPIMAGE="nvim-linux-x86_64.appimage"

# Check if we can save to the download directory.
if [[ ! -d "$DOWNLOADDIR" ]] || [[ ! -w "$DOWNLOADDIR" ]]; then
	echo "Cannot write to $DOWNLOADDIR. Downloading to $HOME/Downloads"
	DOWNLOADDIR="$HOME/Downloads";
fi

# DOWNLOAD the package.
curl --output-dir "$DOWNLOADDIR" -LO "$URL" 
APPPATH="$DOWNLOADDIR/$APPIMAGE"

if [[ ! -f "$APPPATH" ]]; then
	echo "ERROR: didn't download to $APPPATH?"
	exit
fi


# INSTALL the package.
chmod 755 "$APPPATH"
PARENTDIR=$(basename "$TARGETDIR")
if [[ ! -d "$TARGETDIR" ]]; then
	if [[ ! -w "$PARENTDIR" ]]; then
		sudo mkdir -p "$TARGETDIR"
	else
		mkdir -p "$TARGETDIR"
	fi
fi

if [[ ! -w "$PARENTDIR" ]]; then
	sudo mv "$APPPATH" "$TARGETDIR/"
	sudo ln -s "$TARGETDIR/$APPIMAGE" "$TARGETDIR/nvim"
	sudo cp "$SCRIPTPATH" "$TARGETDIR/"
	sudo chown -R root:root "$TARGETDIR"
else
	mv "$APPPATH" "$TARGETDIR/"
	ln -s "$TARGETDIR/$APPIMAGE" "$TARGETDIR/nvim"
	cp "$SCRIPTPATH" "$TARGETDIR/"
fi


# Check that the new install is in the $PATH and prioritize it if it is not.
source "$HOME/.bashrc"
if [[ ":$PATH:" != *":$TARGETDIR:"* ]]; then
	echo 'export PATH="'$TARGETDIR':$PATH"' >> $HOME/.bashrc
	echo "source your ~/.bashrc to test the path or logout/in to your desktop then run: nvim"
	echo "    source ~/.bashrc"
	echo "    nvim"
fi

# EXTRA NOTES
: <<'COMMENT'
# The execution of .appimage files can fail. In that case, extracting the image is needed.

cd "$TARGETDIR"
"$APPPATH" --appimage-extract
mv "$APPPATH/squashfs-root" "$TARGETDIR"
"$TARGETDIR/squashfs-root/AppRun" --version
sudo ln -s "$TARGETDIR/squashfs-root/AppRun" "$TARGETDIR/nvim"
COMMENT

