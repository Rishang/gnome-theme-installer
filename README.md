# Gnome-looks themes cli downloader

## A cli-tool to download & install gnome based Icons, GTK, Cursor themes easily

### Installation

**pre-requisits:** having installed `python3` `curl` `wget` `gnome-tweaks` `unzip`

    sudo apt install -y python3 python3-pip curl wget gnome-tweaks gnome-tweak-tool unzip

**Install `gnomelooks` script**

    bash -c "$(curl -fsSL https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/install.sh)"

## gnomelooks

To Install themes for current user use `gnomelooks`

To Install themes globally use `sudo gnomelooks`

## gnomelooks help Page

    ~$  gnomelook -h


    usage: gnomelooks.py --gtk 'https://www.gnome-look.org/p/1253385/'

    Gnome Theme Downloader - This script downloads - Icon, Shell and Cursor themes form https://www.gnome-look.org/,
    and automatically installs it, Just visit "https://www.gnome-look.org/" copy the url of the theme you want to install
    like the following example above showing, installing - Sweet theme.

    OPTIONS:
    -h, --help      show this help message and exit
    --gtk [URL]     download and install gnome gtk/shell theme.
    --icon [URL]    download and install gnome icon theme.
    --cursor [URL]  download and install gnome cursor theme.
    -ls [ gtk | icon ]         List installed themes
