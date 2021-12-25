#! /usr/bin/python3

import os
import json
import random
import tarfile
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import AnyStr, List, Dict

# pipi
import requests
from colorama import Fore

# locals

# -- code --
this_file_path = Path(os.path.abspath(__file__)).resolve()


def git_pull():
    """pull git repo"""

    if os.path.exists(str(this_file_path.parent) + "/.git"):
        os.chdir(this_file_path.parent)
        os.system("git pull origin main")


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

    def error(self, message: str, stop_here=False):
        print(Fore.RED + "ERROR: " + message + Fore.RESET)
        if stop_here == True:
            exit(1)

    def sucesses(self, message: str):
        print(Fore.LIGHTGREEN_EX + message + Fore.RESET)

    def green(self, message: str):
        print(Fore.GREEN + message + Fore.RESET)

    def warning(self, message: str):
        print(Fore.YELLOW + "WARNING: " + message + Fore.RESET)

    def info(self, message: str):
        print(Fore.LIGHTMAGENTA_EX + "INFO: " + message + Fore.RESET)

    def title(self, message: str):
        print(Fore.LIGHTCYAN_EX + message + Fore.RESET)

    def random_color(self, message: str, **kwargs):
        r_color = random.choice(self.colors)
        print(r_color + message + Fore.RESET, **kwargs)
        return r_color


message = Message()


def ls(path: str, only_dir: bool = False, include_path: bool = False) -> list:
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
            p_ls = [file for file in os.listdir(path) if os.path.isdir(path + f"/{file}")]
    else:
        if include_path:
            p_ls = [path + f"/{file}" for file in os.listdir(path)]
        else:
            p_ls = os.listdir(path)
    
    p_ls.sort()
    return p_ls

def extract(path: str, at: str):
    """Extract tar file"""

    if ".tar" in path:
        with tarfile.open(path) as tar:
            if not os.path.exists(at):
                os.makedirs(at)
            tar.extractall(path=at)
            message.sucesses(f"""Extracted {path}, at {at}""")
            return True
    else:
        message.error(f"{path} is not tar file.")
        return False


def download(url: str, at: str):
    """"""

    file = requests.get(url)

    if not os.path.exists(at):
        os.makedirs(at)

    file_name: str = url.split("/")[-1]
    if file.status_code == 200:
        with open(f"{at}/{file_name}", "wb") as fw:
            fw.write(file.content)
        message.info(f"""Downloaded: {file_name} at {at}""")
        return f"{at}/{file_name}"
    else:
        message.error("status_code {file.status_code}", stop_here=True)
        exit()


def dn_n_extract(url: str, at: str) -> list:
    """Download `url` and extract `at` path."""

    temp = TemporaryDirectory(prefix="looks_ex_", suffix="")
    temp_dn = TemporaryDirectory(prefix="looks_dn_", suffix="")
    
    # Download
    message.info(f"Downloading... \n")
    dp = download(url, at=temp_dn.name)

    # extract at tmp, and list folders
    extract(dp, temp.name)
    extracted_items: list = ls(temp.name, only_dir=True)

    for f in extracted_items:
        at_f = os.path.join(at, f)
        if os.path.exists(at_f):
            shutil.rmtree(at_f)
        shutil.move(os.path.join(temp.name, f), at_f)
        print(f"Moved to: {at_f}")
    
    temp_dn.cleanup()
    temp.cleanup()
    return extracted_items


def tableDict(data: List[Dict], ignore_keys: List[AnyStr] = []):
    """"""

    all: dict = {}

    padding: dict = {}

    _keys = []
    for d in data:
        # print(d.keys())
        for i in d.keys():
            if i not in _keys:
                _keys.append(i)

    for ik in ignore_keys:
        if ik in _keys:
            _keys.remove(ik)

    for d in data:
        for i in _keys:
            _value = d.get(i, "")
            if all.get(i):
                all[i] += [_value]
                # for table padding
                padding[i] += [len(f"{_value}")]
            else:
                all[i] = [_value]

                # for table padding
                padding[i] = [len(f"{_value}")]

    for i in padding:
        padding[i] = max(padding[i])

    return all, padding


def print_table(data: List[Dict], ignore_keys: List = []):
    """"""

    table, padding = tableDict(data, ignore_keys)
    underline: int = 0

    if len(data) <= 0:
        return

    # print column
    for key in table:
        if len(key) < padding[key]:
            pd = padding[key]
        else:
            pd = len(key)

        msg = f"{key.upper():<{pd}} | "
        underline += len(msg)

        # message.random_color(msg, end='')
        print(Fore.BLUE + msg + Fore.RESET, end="")

    print()
    print(Fore.LIGHTYELLOW_EX + "-" * (underline - 1))

    # print rows
    for i in range(len(table[key])):
        for key in table.keys():
            if len(key) < padding[key]:
                pd = padding[key]
            else:
                pd = len(key)
            # print(_pd)
            message.random_color(f"{table[key][i]:<{pd}} | ", end="")
        print()
