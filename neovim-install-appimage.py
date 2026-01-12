#!/usr/bin/env python3
"""Download the official app image for neovim and set it up for use."""
from argparse import ArgumentParser
from os import (access, W_OK, environ)
from pathlib import Path
from re import match
from requests import get
from shutil import which
from subprocess import run
from sys import executable
from sys import exit as exit_with_error
from tempfile import NamedTemporaryFile
from textwrap import dedent
from urllib.parse import urlparse

args = None
app_image = None
download_path = None

def parse_aguments():
    """Parses all the commandline arguments"""
    global args
    parser = ArgumentParser(
        prog='neovim-install-appimage',
        description='A simple script to install neovim from the offical AppImage.')
    parser.add_argument('-p', '--path',
        type=Path,
        default=Path('/opt/nvim'),
        help='The install path for the AppImage file.')
    parser.add_argument('-t', '--temp',
        type=Path,
        default=Path.home() / 'Downloads',
        help='The temporary download folder for the AppImage file.')
    parser.add_argument('-u', '--url',
        type=str,
        default='https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.appimage',
        help='The download URL for the AppImage.')
    parser.add_argument('-a', '--appimage',
        type=str,
        help='The name of the AppImage file. The default will attempt to be gathered from the URL. It will be normalized to end in .appimage and default to nvim-linux-x86_64.appmage if parsing the URL fails or this parameter is empty.')
    args = parser.parse_args()
    

def has_desktop_environment():
    """Checks if the current execution is within a desktop environment"""
    return environ.get('DISPLAY') != None or environ.get('WAYLAND_DISPLAY') != None


def set_appimage(*, default=None):
    """Sets the target app_image file name"""
    global app_image
    url_parts = urlparse(args.url)
    rx = r".*\.appimage"
    # Check if the parsed url path matches *.appimage. If it doesn't, use the user override or the default.
    if match(rx, url_parts.path):
        app_image = Path(url_parts.path).name
        return
    elif args.appimage != None and match(rx, args.appimage):
        app_image = args.appimage
        return
    elif default != None and match(rx, default):
        app_image = default
        return
    exit_with_error('AppImage name could not be parsed to match *.appimage.')


def download(*, url=None):
    """Downloads the url specified to to the download_dir"""
    global app_image, download_path
    download_dir = args.temp
    if not access(args.temp, W_OK):
        download_dir = Path().home()
        if not access(download_dir, W_OK):
            exit_with_error(f"Cannot write to {download_dir}")
    if url != None:
        download_path = download_dir / app_image
        response = get(url)
        if response.status_code == 200:
            with open(download_path, 'wb') as file:
                file.write(response.content)
            return
    exit_with_error(f"Failed to download {url} to {download_path}")


def install(*,path=None, symlink=None):
    """Installs the downloaded file to the path. It will request elevation if there are not enough permissions to path."""
    if download_path == None:
        exit_with_error('Install called before download validated.')
    elif path == None:
        exit_with_error('Install called with no path.')
    with NamedTemporaryFile(mode='w+t') as temp_file:
        command = [executable, temp_file.name]
        # Pick elevation binary if no permissions to write to target path.
        # AppImage are linux only, not importing a third party module just to do this silly task.
        if not path.exists() and not access(path.parent, W_OK) or path.exists() and not access(path, W_OK):
            message = 'Install path not writable, attempting to install with sudo.'
            for alertbin in [
                ['zenity', '--info', '--text', message],
                ['kdialog', '--msgbox', message],
                None]:
                if not has_desktop_environment() and alertbin == None:
                    print(message)
                    break
                elif which(alertbin[0]):
                    run(alertbin, shell=False)
                    break
            for sudo in ['pkexec', 'gksudo', 'kdesudo', 'sudo']:
                if not has_desktop_environment():
                    command.insert(0, 'sudo')
                    break
                elif which(sudo):
                    command.insert(0, sudo)
                    break
        # Looking at the various options, this seemed about right to keep it as 'python' and still allow elevating.
        # Doing this short subscript as pure bash would probably be smarter, all paths are already validated.
        script = dedent(f"""\
            from os import (chmod, chown, remove, symlink)
            from pathlib import Path
            from shutil import move
            target_path = Path("{str(path)}")
            app_image_path = Path("{str(path/app_image)}")
            symlink_path = Path("{str(path/symlink)}")
            if not target_path.exists():
                target_path.mkdir()
            move("{str(download_path)}", app_image_path)
            chown(app_image_path, user='root', group='root')
            chmod(app_image_path, 0o755)
            if "{str(symlink)}" != None:
                if symlink_path.is_symlink():
                    remove(symlink_path)
                symlink("{str(app_image)}", symlink_path)
            """)
        temp_file.write(script)
        temp_file.seek(0)
        result = run(command, shell=False)
        if result.returncode != 0:
            exit_with_error(f"Failed to install {download_path} to {path/app_image}")


def add_to_path(*, bin_dir=None):
    """Check that the new install is in the $PATH and prioritize it if it is not."""
    if bin_dir == None:
        exit_with_error(f"bin_dir not specified")
    bashrc = Path.home()/'.bashrc'
    if not f":{bin_dir}:" in f":{environ['PATH']}:":
        with open(bashrc, 'a+') as file:
            file.seek(0)
            content = file.read()
            if not f"PATH=\"{bin_dir}" in content:
                file.write(f"export PATH=\"{bin_dir}:$PATH\"\n")


parse_aguments()
if __name__ == "__main__":
    set_appimage(default='nvim-linux-x86_64.appimage')
    download(url=args.url)
    install(path=args.path, symlink='nvim')
    add_to_path(bin_dir=args.path)
