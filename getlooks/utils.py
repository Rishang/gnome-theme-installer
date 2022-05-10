#! /usr/bin/python3

import os
import json
import random
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import AnyStr, List, Dict
import logging

# pipi
import requests
from colorama import Fore
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.logging import RichHandler
from rich import print as rprint

# locals
console = Console()

# -- code --
this_file_path = Path(os.path.abspath(__file__)).resolve()


def _logger(debug_flag: str = ""):

    # message
    flag = os.environ.get(debug_flag)
    logger = logging.getLogger(__name__)

    if flag == None:
        logger.setLevel(logging.INFO)
    elif flag == "debug":
        logger.setLevel(logging.DEBUG)
    elif flag == "warning":
        logger.setLevel(logging.WARNING)
    elif flag == "info":
        logger.setLevel(logging.INFO)

    handler = RichHandler(log_time_format="")
    logger.addHandler(handler)
    return logger


logger = _logger(debug_flag="TEST_THEME_INSTALLER")

_colors = {
    "green": "#8CC265",
    "light_green": "#D0FF5E bold",
    "blue": "#4AA5F0",
    "cyan": "#76F6FF",
    "yellow": "#F0A45D bold",
    "red": "#E8678A",
    "purple": "#8782E9 bold",
}


class JsonState:

    cache: Dict[str, Dict] = dict()
    cache_path: str = ""

    def add(self, key: str, data: dict, dublicate: bool = False):

        if not dublicate:
            if key not in self.cache.keys():
                self.cache[key] = data
        else:
            self.cache[key] = data

    def put(self, key: str, data: dict) -> bool:
        # , where:dict={}

        if len(self.cache) == 0:
            self.add(key, data)
            return True

        if key != None:
            keys = self.cache[key].keys()

        if not keys == data.keys():
            print("old keys: ", keys)
            print("new keys: ", data.keys())
            raise ValueError("previos key datakeys not match")

        self.cache[key] = data
        return True

    def load(self, cache_path: str):
        if not cache_path.split(".")[-1] == "json":
            raise ValueError("expected json file")

        elif not os.path.exists(cache_path):
            self.cache_path = cache_path
            return

        if not os.path.getsize(cache_path) == 0:

            with open(cache_path, "r") as c:
                data = json.loads(c.read())
                self.cache = data

        self.cache_path = cache_path

    def reload(self):
        self.load(self.cache_path)

    def save(self):
        parent_dir = os.path.dirname(self.cache_path)

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with open(self.cache_path, "w") as c:
            data = json.dumps(self.cache, indent=4)
            c.write(data)
            print(f"Updated state: {self.cache_path}")
            return True


class Message:
    """Print message of type and color"""

    colors = [
        Fore.WHITE,
        # blue
        Fore.BLUE,
        Fore.LIGHTBLUE_EX,
        # green
        Fore.GREEN,
        Fore.LIGHTGREEN_EX,
        # cyan
        Fore.CYAN,
        Fore.LIGHTCYAN_EX,
        # red
        # Fore.RED,
        Fore.LIGHTRED_EX,
        # magenta
        Fore.MAGENTA,
        Fore.LIGHTMAGENTA_EX,
        # yellow
        Fore.YELLOW,
        Fore.LIGHTYELLOW_EX,
    ]

    def __init__(self):
        pass

    def sucesses(self, message: str):
        print(Fore.LIGHTGREEN_EX + message + Fore.RESET)

    def random_color(self, message: str, **kwargs):
        r_color = random.choice(self.colors)
        print(r_color + message + Fore.RESET, **kwargs)
        return r_color


message = Message()


def ls(
    path: str,
    only_dir: bool = False,
    include_path: bool = False,
    ignore_items: list = [],
) -> list:
    """List files and directories of given path"""

    if not os.path.exists(path):
        raise Exception(f"Path: {path} not found")
    if only_dir:
        if include_path:
            p_ls = [
                path + f"/{file}"
                for file in os.listdir(path)
                if os.path.isdir(path + f"/{file}")
            ]
        else:
            p_ls = [
                file for file in os.listdir(path) if os.path.isdir(path + f"/{file}")
            ]
    else:
        if include_path:
            p_ls = [path + f"/{file}" for file in os.listdir(path)]
        else:
            p_ls = os.listdir(path)

    for item in ignore_items:
        if item in p_ls:
            p_ls.remove(item)

    p_ls.sort()
    return p_ls


def extract(path: str, at: str):
    """Extract tar file"""
    try:
        shutil.unpack_archive(path, at)
        logger.debug(f"""Extracted {path}, at {at}""")
        return True
    except:
        logger.error(f"can't extract: {path}")
        raise Exception("Invalid file to extract")


def download(url: str, at: str):
    """"""

    file = requests.get(url, stream=True)

    if not os.path.exists(at):
        os.makedirs(at)

    file_name: str = url.split("/")[-1]
    if file.status_code == 200:
        with open(f"{at}/{file_name}", "wb") as fw:
            fw.write(file.content)
        logger.debug(f"""Downloaded: {file_name} at {at}""")
        return f"{at}/{file_name}"
    else:
        logger.error(f"request status_code: {file.status_code}")
        exit(1)


def dn_n_extract(url: str, at: str) -> list:
    """Download `url` and extract `at` path."""

    temp = TemporaryDirectory(prefix="looks_ex_", suffix="")
    temp_dn = TemporaryDirectory(prefix="looks_dn_", suffix="")

    # Download
    logger.info(f"Downloading... \n")
    dp = download(url, at=temp_dn.name)

    # extract at tmp, and list folders
    extract(dp, temp.name)
    extracted_items: list = ls(temp.name, only_dir=True)

    for f in extracted_items:
        at_f = os.path.join(at, f)
        if os.path.exists(at_f):
            shutil.rmtree(at_f)
        shutil.move(os.path.join(temp.name, f), at_f)
        rprint(f"[green]Moved to:[reset] {at_f}")

    temp_dn.cleanup()
    temp.cleanup()
    return extracted_items


def dict_list_tbl(items=list[dict], ignore_keys: list = []):
    keys = []
    data = []

    for item in items:
        _tmp: tuple = ()
        for key in [i for i in item.keys() if i not in ignore_keys]:

            if key not in keys:
                keys.append(key)
            _tmp += (str(item[key]),)
        data.append(_tmp)

    return keys, data


def show_table(
    data: List[Dict], ignore_keys: List = [], title: str = "", border_style=""
):
    """rich table"""

    text = Text(title, style=_colors["light_green"])

    print()

    table = Table(title=text, style=_colors["purple"], border_style=border_style)
    columns, rows = dict_list_tbl(data, ignore_keys)

    colors = {
        0: _colors["yellow"],
        1: _colors["red"],
        2: _colors["green"],
        3: _colors["cyan"],
        4: _colors["blue"],
    }

    for count, col in enumerate(columns):
        color = colors[count % len(colors)]
        table.add_column(col, justify="left", style=color, no_wrap=True)
    for row in rows:
        table.add_row(*row)

    console = Console()
    console.print(table)
