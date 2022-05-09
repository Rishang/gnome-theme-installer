#! /usr/bin/python3

import dataclasses
import os
import shutil
from typing import List
from copy import deepcopy
from colorama import Fore

# local
from getlooks.looks_path import STATE_PATH
from getlooks.utils import JsonState, JsonState, dn_n_extract, show_table, logger
from getlooks.core import (
    ProductInfo,
    DeskEnv,
    scrapGnomeLooks,
    message,
    product_state_cache,
    path_for,
)

# -- code --

desk = DeskEnv()

if os.environ.get("TEST_THEME_INSTALLER") == "true":
    state_path = f"./test/state.json"
else:
    state_path = f"{desk.HOME}/{STATE_PATH}-{desk.USER}/state.json"


def get_path(product: ProductInfo) -> str:

    # print(product.type)

    if os.environ.get("TEST_THEME_INSTALLER") == "true":
        path = "./themes/" + product.type
    elif product.type == "Global Themes" and desk.DESK_ENV == "kde":
        path = desk.theme_path("kde_global")
    else:
        if product.type in path_for:
            path = desk.theme_path(path_for[product.type])
        else:
            message.warning("Can't identify product category, using current path.")
            path = "."
    return path


def state_update_rm(removed_items: List[str]):
    state = JsonState()

    state.load(state_path)
    _products = product_state_cache(state.cache)
    products = deepcopy(_products)

    for path in removed_items:
        file_name = path.split("/")[-1]
        for _id in _products:
            product = products[_id]
            if len(product.files) == 1 and len(product.files[0].extracted_files) == 1:
                if file_name in product.files[0].extracted_files:
                    products.pop(_id)
                    continue

            for _f in product.files:

                if file_name in _f.extracted_files:
                    if len(_f.extracted_files) == 1:
                        product.files.remove(_f)
                    else:
                        _f.extracted_files.remove(file_name)
    # update state
    for _id in products:
        logger.debug(products[_id])
        state.cache[_id] = dataclasses.asdict(products[_id])

    for _id in list(state.cache.keys()):
        if _id not in products.keys():
            state.cache.pop(_id)

    state.save()
    return state


def looks_list(themes: bool = False, icons: bool = False):
    state = JsonState()
    state.load(state_path)

    logger.debug(f"state_path: {state_path}")

    products = product_state_cache(state.cache)

    dirs: List[str] = []
    for p in products:
        product = products[p]
        if themes and product.is_theme():
            dirs += [file for f in product.files for file in f.extracted_files]
        elif icons and (product.is_icon() or product.is_cursor()):
            dirs += [file for f in product.files for file in f.extracted_files]

    return (dirs, products)


def looks_rm(themes: bool = False, icons: bool = False) -> List[str]:
    """Remove theme folder and update the state"""
    _look_list, products = looks_list(themes, icons)

    if len(_look_list) == 0:
        return []
    theme_path = products[list(products.keys())[0]].install_path

    show_table(
        [{"id": i, "names": _look_list[i]} for i in range(len(_look_list))],
        title="Remove theme",
    )
    print("Enter id, of file to remove")
    data: list = input().split(",")

    removed_items = []
    for f in data:
        li = _look_list[int(f)]
        try:
            item = f"{theme_path}/{li}"
            logger.debug(f"removing {item}")
            shutil.rmtree(path=item)
        except FileNotFoundError:
            ...
        logger.debug(li)
        removed_items.append(li)

    # remove item and update state
    logger.debug(removed_items)
    state_update_rm(removed_items)

    return removed_items


def looks_log(product: ProductInfo):

    state = JsonState()
    state.load(state_path)

    cache_products = product_state_cache(state.cache)

    if len(cache_products) != 0:
        for i in cache_products:
            if cache_products[i].url == product.url:
                final = []
                tmp = []
                for f in product.files + cache_products[i].files:
                    if f.name not in tmp:
                        tmp.append(f.name)
                        final.append(f)

                product.files = final
                _d = dataclasses.asdict(product)
                state.put(key=product.project_id, data=_d)
            else:
                _d = dataclasses.asdict(product)
                state.add(key=product.project_id, data=_d)
    else:
        _d = dataclasses.asdict(product)
        state.add(key=product.project_id, data=_d)

    state.save()


def looks_install(url, p_ids: List[str] = []) -> ProductInfo:

    """
    valid list for theme download
    [   "www.opendesktop.org/",
        "www.pling.com/",
        "store.kde.org/",
        "www.gnome-look.org/",
        "www.xfce-look.org/",    ]
    """

    if "gnome-look" in url:
        desk.DESK_ENV = "gnome"
    elif "kde.org" in url:
        desk.DESK_ENV = "kde"
    elif "xfce-look" in url:
        desk.DESK_ENV = "xfce"
    else:
        desk.check_env()

    product = scrapGnomeLooks(url)

    message.random_color(f"\nTheme-Name:  {product.title}", end="")
    message.random_color(f"\nType: {product.type}", end="")
    message.random_color(f"\tLikes: {product.likes}", end="")
    message.random_color(f"\tCreator: {product.author}\n")

    data = []
    for i in product.files:
        data.append(vars(i))
    show_table(
        data=data,
        ignore_keys=["type", "is_active", "url", "extracted_files"],
        title="Install Themes/Icons",
    )

    path = get_path(product)
    product.install_path = path

    print(f"{Fore.LIGHTBLUE_EX}\nEnter ids from above table,\nOf the files you want to download: {Fore.RESET}", end="")
    if len(p_ids) == 0:
        p_ids = input().split(",")
    files = []
    for p_id in p_ids:
        _id = int(p_id)
        theme_files = dn_n_extract(product.files[_id].url, product.install_path)

        # extra var
        product.files[_id].extracted_files = theme_files
        files.append(product.files[_id])

    product.files = files

    return product


def looks_update():

    state = JsonState()
    desk.check_env()

    state.load(state_path)

    if len(state.cache) == 0:
        message.error(
            "No themes installed,"
            + f"you need to install a theme first. check state: {state_path}"
            "",
            stop_here=True,
        )

    cache_products = product_state_cache(state.cache)

    for p_id in cache_products:
        _c_product = cache_products[p_id]
        product = scrapGnomeLooks(_c_product.url)
        product.install_path = _c_product.install_path

        message.sucesses(f"Fetching: {_c_product.url} ")

        _files: list = []
        for c_fi in _c_product.files:

            # latest product files -> _l_fi
            for l_fi in product.files:
                if l_fi.name == c_fi.name:

                    if l_fi.date() > c_fi.date():
                        _id = int(l_fi.id)
                        ex_files = dn_n_extract(
                            product.files[_id].url, product.install_path
                        )
                        l_fi.extracted_files = ex_files
                        _files.append(l_fi)
                    else:
                        _files.append(c_fi)
                        message.info(f"No updates: {c_fi.name} ")
                        continue

        product.files = _files

        _d = dataclasses.asdict(product)
        state.put(key=p_id, data=_d)

    state.save()
