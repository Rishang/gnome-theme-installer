#! /usr/bin/python3
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# pipi
from colorama import Fore
import typer

# local
from getlooks.utils import message, show_table
from getlooks.looks import looks_install, looks_list, looks_rm, looks_log, looks_update
from getlooks.core import DeskEnv


def see_help(arg: str = "", stop_here: bool = True):
    return message.error(
        "This command required arguments, use "
        + Fore.LIGHTYELLOW_EX
        + f"{arg} --help"
        + Fore.RED
        + " to see them"
        + Fore.RESET,
        stop_here,
    )


app = typer.Typer(
    help=f"{Fore.LIGHTGREEN_EX} Theme Installer for Gnome, Xfce4, Kde {Fore.RESET}"
)


@app.command()
def get(url: str = typer.Argument(None, help="looks or pling [URL] of theme/icon")):
    """
    | Install new UI themes/icons
    """

    if url is None or url == "":
        see_help("get")

    product = looks_install(url)
    looks_log(product)


@app.command()
def update(
    me: bool = typer.Option(False, "--me", help="Update tool itself"),
    themes: bool = typer.Option(
        False, "-t", "--themes", help="Update all gtk/icon themes"
    ),
):
    """
    | Update installed themes and icons via this tool
    """

    if me:
        os.system("pip install -U gnomelooks")
    elif themes:
        looks_update()
    else:
        see_help("update")


@app.command()
def rm(
    themes: bool = typer.Option(False, "-t", "--themes", help="To remove Themes"),
    icons: bool = typer.Option(False, "-i", "--icons", help="To remove Icons"),
):
    """
    | Remove installed themes and icons
    """
    if themes:
        looks_rm(themes=True)
    elif icons:
        looks_rm(icons=True)
    else:
        see_help("rm")


@app.command()
def askenv():
    """
    | ask deskenv
    """
    denv = DeskEnv()
    denv.env_prompt()


@app.command()
def ls(
    themes: bool = typer.Option(False, "-t", "--themes", help="To list Themes]"),
    icons: bool = typer.Option(False, "-i", "--icons", help="To list Icons]"),
):
    """
    | List installed themes and icons
    """
    print()
    if (themes or icons) != True:
        see_help("ls")

    _look_list = looks_list(themes=themes, icons=icons)[0]

    title = "Theme names"
    if icons:
        title = "Icon names"

    show_table(
        data=[{"id": i, "names": _look_list[i]} for i in range(len(_look_list))],
        title=title,
    )
    print()


if __name__ == "__main__":
    app()
