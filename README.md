# Gnome-looks themes cli downloader

## A cli-tool to download & install gnome based Icons, GTK, Cursor themes easily

![image 1](https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/.github/images/1.png)

![image 2](https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/.github/images/2.png)

## gnomelooks

To Install themes for current user `gnomelooks -i [URL]`

To Install themes globally `sudo gnomelooks -i [URL]`

## gnomelooks help Page

    ~$  gnomelooks -h
        usage: gnomelooks [OPTIONS] [URL]

        Example: gnomelooks -i 'https://www.gnome-look.org/p/1253385/'

        Gnome Theme Downloader - This script downloads - Icon, Shell and Cursor themes form https://www.gnome-look.org/, and
        automatically installs it, Just visit "https://www.gnome-look.org/" copy the url of the theme you want to install like
        the following example above showing, installing - Sweet theme.

        OPTIONS:
        -h, --help            show this help message and exit
        -i [URL]              Install gnome - GTK/Shell ,Icon, Cursor theme.
        -update [Any string]  Update this tool
        -ls [gtk | icon]      list installed themes
        -rm theme name        remove any installed themes

### Installation

    pip3 install -U gnomelooks

## update gnomelooks

run: `gnomelooks -update me`
