# Gnome-looks themes cli downloader

[![Installs](https://static.pepy.tech/personalized-badge/gnomelooks?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/gnomelooks) ![Release version](https://img.shields.io/github/v/release/Rishang/gnome-theme-installer.svg?style=flat-square
)
[![Python Version](https://img.shields.io/badge/Python-3.10-xx.svg)](https://shields.io/)

**A cli-tool to install and update gnome based Icons, GTK, Cursor themes easily**

### Supported desktop environments

- **Gnone**
- **Xfce**
- **KDE Plasma**

![image 1](./.github/images/get.png)

## gnomelooks cli usage


- To Install themes for current user
        
        gnomelooks get [THEME-URL]

- To Install themes globally

        sudo gnomelooks get [THEME-URL]

### Installation

    pip3 install -U gnomelooks

## gnomelooks help Page

    ~$ gnomelooks --help
        Usage: gnomelooks [OPTIONS] COMMAND [ARGS]...

        Theme Installer for Gnome, Xfce4, Kde 

        Options:
        --install-completion  Install completion for the current shell.
        --show-completion     Show completion for the current shell, to copy it or
                                customize the installation.
        --help                Show this message and exit.

        Commands:
        askenv  | ask deskenv
        get     | Install new UI themes/icons
        ls      | List installed themes and icons
        rm      | Remove installed themes and icons
        update  | Update installed themes and icons via this tool

## update all themes and icons

Run: `gnomelooks update --themes`
