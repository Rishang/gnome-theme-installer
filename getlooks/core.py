#! /usr/bin/python3

import re
import os
from pathlib import Path
import json
import base64
from datetime import datetime
from urllib.parse import unquote
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# pipi
import requests
from bs4 import BeautifulSoup
from requests.api import patch

# local
from getlooks.utils import show_table, message
from getlooks.looks_path import DESK_THEME_PATH, STATE_PATH


path_for = {
    "GTK3/4 Themes": "themes",
    "Full Icon Themes": "icons",
    "Cursors": "cursors",
}


@dataclass
class FileInfo:
    """
    Content related file info details
    """

    id: str
    name: str
    type: str
    is_active: bool
    url: str
    size: str
    downloads: int
    changed_at: str
    extracted_files: Optional[List[str]] = field(default_factory=list[str])

    def __post_init__(self):
        if isinstance(self.url, str):
            self.url = unquote(self.url)

    def date(self) -> datetime:
        return datetime.strptime(self.changed_at, "%Y-%m-%d %H:%M:%S")


@dataclass
class ProductInfo:
    """
    Content related theme page details
    """

    type: str
    project_id: str
    author: str
    description: str
    title: str
    likes: str
    changed_at: str
    system_tags: List[str]
    files: List[FileInfo]
    version: Optional[str] = ""
    url: Optional[str] = field(default_factory=str)
    install_path: Optional[str] = field(default_factory=str)

    def date(self) -> datetime:
        return datetime.strptime(f"{self.changed_at}", "%Y-%m-%d %H:%M:%S")

    def __is_type(self, expect: str):
        type = path_for.get(self.type)
        if type != None and type == expect:
            return True
        else:
            return False

    def is_icon(self):
        return self.__is_type("icons")

    def is_theme(self):
        return self.__is_type("themes")

    def is_cursor(self):
        return self.__is_type("cursors")

    # def __post_init__(self):
    #     files = []
    #     for file in self.files:
    #         if not isinstance(FileInfo, file):
    #             _f = FileInfo(**file)
    #             files.append(_f)
    #         else:
    #             files.append(file)
    #     self.files = files


class DeskEnv:
    """
    Check desktop env:
    - gnome
    - kde
    - xfce4
    and set theme path based on above env
    """

    USER = os.environ.get("USER")
    SUDO_USER = os.environ.get("SUDO_USER")
    HOME = (SUDO_USER and f"/home/{SUDO_USER}") or os.environ.get("HOME")
    DESK_ENV = ""
    state_file = Path(f"{HOME}/{STATE_PATH}-{USER}/deskenv")
    valid_env = {
        "1": "gnome",
        "2": "kde",
        "3": "xfce",
    }

    def __init__(self):
        if os.path.isfile(self.state_file):
            with open(self.state_file, "r") as s:
                state = s.read()
                self.DESK_ENV = state.strip()

    def env_prompt(self):

        if not os.path.isdir(self.state_file.parent):
            os.makedirs(self.state_file.parent)

        message.error("Can't figureout desktop environment")
        message.title(
            "Which one is your desktop environment ?\n"
            "\nChoose you desktop environment id, \nExample: 1 for gnome\n"
        )
        show_table([self.valid_env], title="Select desktop environment")

        print("\nEnter id for your desktop environment to continue: ", end="")
        ans = int(input())
        if ans <= len(self.valid_env):
            self.DESK_ENV = self.valid_env[str(ans)]
            with open(self.state_file, "w") as denv:
                denv.write(f"{self.DESK_ENV}")
        else:
            exit(1)

    def check_env(self):
        """Updates self.DESK_ENV according to your desk env"""

        if len(self.DESK_ENV) != 0:
            return

        # read /proc/sched_debug
        XDG_DESK = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get(
            "ORIGINAL_XDG_CURRENT_DESKTOP"
        )
        if XDG_DESK:
            # print(XDG_DESK)
            ps = f"{XDG_DESK}".lower()

            if re.search("gnome", ps):
                self.DESK_ENV = self.valid_env["1"]
            elif re.search("plasma|kde", ps):
                self.DESK_ENV = self.valid_env["2"]
            elif re.search("xfce", ps):
                self.DESK_ENV = self.valid_env["3"]
            else:
                self.env_prompt()
        else:
            self.env_prompt()

    def theme_path(self, theme_type):
        """
        set the path for themes
        `theme_type` -> `themes` or `icons` or `cursor`
        """

        USER = self.USER
        _d = DESK_THEME_PATH[self.DESK_ENV]

        # arg = (themes or icons or cursor)
        if theme_type in _d.keys():
            if USER == "root":
                path = _d[theme_type]["global"]
            else:
                path = _d[theme_type]["local"]

        elif theme_type == "kde_global" and self.DESK_ENV == "kde":
            if USER == "root":
                path = _d["global_theme"]["global"]
            else:
                path = _d["global_theme"]["local"]
        else:
            raise ValueError(f"got unexpected theme_type -> {theme_type} ")

        return path.replace("~", self.HOME)


def scrapGnomeLooks(url):
    """"""

    try:
        gnome_looks_page = requests.get(url, timeout=30)
    except requests.exceptions.ConnectTimeout:
        raise Exception(f"Connection timeout {url}")

    if gnome_looks_page.status_code == 404:
        message.error("Page responded 404 (File not found)", stop_here=True)
        exit()

    soup = BeautifulSoup(gnome_looks_page.text, "lxml")

    # where a variable contain json data of theme-files

    # product details
    pattern = r"productViewDataEncoded = '(ey.+)';var categoryId"

    # if api-json is not present at jspath, bruteforce for jspath
    script_child = [n for n in range(10, 26)]
    for blind_id in script_child:
        try:
            productData = soup.select_one(
                f"#od-body > script:nth-child({blind_id})"
            ).string
            p = re.search(pattern, productData)[1]
            p = base64.decode(p)

            if re.search(pattern, productData):
                EXIT_FLAG = False
                break
        except:
            EXIT_FLAG = True
            continue

        if EXIT_FLAG == True:
            message.error("variable productViewDataEncoded: not found in source code")
            exit(1)

    _p = base64.b64decode(p).decode("utf-8")

    # todict
    p_info = json.loads(_p)
    f_info = json.loads(requests.get(url + "/loadFiles").text)

    # dataclasses
    f_list: List[FileInfo] = []
    count = 0

    system_tags = [t["tag_name"] for t in p_info["systemTags"]]

    for _f in f_info["files"]:
        __t = {
            "id": f"{count}",
            # "g_id": _f["id"],
            "is_active": bool(int(_f["active"])),
            "name": _f["name"],
            "type": _f["type"],
            "url": _f["url"],
            "changed_at": _f["updated_timestamp"],
            "downloads": _f["downloaded_count_uk"],
            "size": f"{int(_f['size'])/1000000}"[:4] + " Mb",
        }
        if __t["is_active"]:
            f_list.append(FileInfo(**__t))
            count += 1

    __p_info = {
        "type": p_info["product"]["cat_title"],
        "project_id": p_info["product"]["project_id"],
        "author": p_info["product"]["username"],
        "description": p_info["product"]["description"],
        "title": p_info["product"]["title"],
        "likes": p_info["tabCnt"]["cntLikes"],
        "version": p_info["product"]["version"],
        "changed_at": p_info["product"]["changed_at"],
        "system_tags": system_tags,
        "files": f_list,
        "url": url,
    }

    # theme file

    # collect active files and ignore archived ones.
    return ProductInfo(**__p_info)


def product_state_cache(data: Dict[str, dict]) -> Dict[str, ProductInfo]:

    products: Dict[str, ProductInfo] = dict()
    for p in data:
        product = ProductInfo(**data[p])
        product.files = [FileInfo(**f) for f in data[p]["files"]]
        products[product.project_id] = product

    return products
