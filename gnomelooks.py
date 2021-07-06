#! /usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import json, csv
import os, shutil
import argparse
from colorama import Fore
import tarfile


class Message:
    def __init__(self):
        pass

    def error(self, message: str, stop_here=False):
        print(Fore.RED + "ERROR: " + message + Fore.RESET)
        if stop_here == True:
            exit(1)

    def sucesses(self, message: str):
        print(Fore.GREEN + message + Fore.RESET)

    def warning(self, message: str):
        print(Fore.YELLOW + "WARNING: " + message + Fore.RESET)

    def info(self, message: str):
        print(Fore.LIGHTMAGENTA_EX + "INFO: " + message + Fore.RESET)

    def title(self, message: str):
        print(Fore.LIGHTCYAN_EX + message + Fore.RESET)


message = Message()


def check_desktop_environment():

    desk_env = {1: "gnome", 2: "kde", 3: "xfce"}

    # read /proc/sched_debug
    if os.path.exists("/proc/sched_debug"):
        with open("/proc/sched_debug", "r") as sched:
            ps = sched.read()

        if "gnome-shell" in ps:
            return desk_env[1]
        elif "plasmashell" in ps:
            return desk_env[2]
        elif "xfce4-session" in ps:
            return desk_env[3]
    else:
        message.error("Can't figureout desktop environment")
        message.title("Which one is your desktop environment \n")

        print("id| Name")
        print("--+-------")
        for e in desk_env:
            print(f" {e}| {desk_env[e].capitalize()}")

        print("\nEnter id for your desktop environment: ", end="")
        ans = int(input())
        if ans >= len(desk_env):
            return desk_env[ans]
        else:
            exit(1)


USER = os.environ.get("USER")
SUDO_USER = os.environ.get("SUDO_USER")
HOME = (SUDO_USER and f"/home/{SUDO_USER}") or os.environ.get("HOME")
DESKTOP_SESSION = check_desktop_environment()


def scrapGnomeLooks(url):

    gnome_looks_page = requests.get(url)
    if gnome_looks_page.status_code == 404:
        message.error("Page responded 404 (File not found)", stop_here=True)
        exit()

    soup = BeautifulSoup(gnome_looks_page.text, "lxml")

    # where a variable contain json data of theme-files
    try:
        apiData = soup.select_one("#od-body > script:nth-child(20)").string
        re.search(r"filesJson = ", apiData)

    except TypeError:
        EXIT_FLAG = False
        # if api-json is not present at jspath, bruteforce for jspath
        script_child = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        for blind_id in script_child:
            try:
                apiData = soup.select_one(
                    f"#od-body > script:nth-child({blind_id})"
                ).string
                if re.search(r"filesJson = \[", apiData):
                    EXIT_FLAG = False
                    break
            except:
                EXIT_FLAG = True
                continue

        if EXIT_FLAG == True:
            message.error("variable filejson: not found in source code")
            exit(1)

    # product info
    product = re.search(r"product = ({.*})", apiData)[1]

    # collect filesJson -> list having json data in it
    filesJson = re.search(r"filesJson = (\[.*\])", apiData)[1]

    # collect active files and ignore archived ones.
    def collect_active(jsonList):

        active = []
        for i in range(len(jsonList)):
            if jsonList[i]["active"] == "1":
                active.append(jsonList[i])
        return active

    return json.loads(product), collect_active(json.loads(filesJson))


# print scraped data in form of tables
def printTable(activeList):

    # get max_len_filename, to calc the area needed to printTable()
    len_filename = []

    for i in range(len(activeList)):
        len_filename.append(len(activeList[i]["name"]))
    max_len_filename = max(len_filename) + 1

    message.title(
        f"""\n{"Id":<4}| {"Filename":<{max_len_filename}}| {"Date":<10} | {"Downloads":<10}| {"Size":<8} |"""
    )
    print("-" * (4 + max_len_filename + 10 + 10 + 8 + 11))

    for i in range(len(activeList)):

        filename = activeList[i]["name"]
        updated_timestamp = activeList[i]["updated_timestamp"][:10]
        downloaded_count = activeList[i]["downloaded_count"]
        sizeMB = round(int(activeList[i]["size"]) / 1000000, 3)

        print(
            Fore.LIGHTRED_EX
            + f"{i:<4}"
            + "| "
            + Fore.GREEN
            + f"{filename:<{max_len_filename}}"
            + "| "
            + Fore.CYAN
            + f"{updated_timestamp:<10}"
            + " | "
            + Fore.YELLOW
            + f"{downloaded_count:<10}"
            + "| "
            + Fore.MAGENTA
            + f"{sizeMB:<6}MB"
            + " |"
        )

    print("-" * (4 + max_len_filename + 10 + 10 + 8 + 11))


# save csv log of downloaded files
def log(filename, date, path, url):

    logFile = f"{HOME}/.gnomelooks/gnomelooks_log.csv"
    logFile_exist = os.path.isfile(logFile)

    with open(logFile, "a+") as csv_log:
        fieldname = ["FILENAME", "DATE", "PATH", "PAGE"]
        writer = csv.DictWriter(csv_log, fieldnames=fieldname)

        if not logFile_exist:
            writer.writeheader()

        writer.writerow({"FILENAME": filename, "DATE": date, "PATH": path, "PAGE": url})
        print(f"Logs saved at: {logFile}")
        if USER == "root":
            SUDO_GID = int(os.environ.get("SUDO_GID"))
            SUDO_UID = int(os.environ.get("SUDO_UID"))
            os.chown(logFile, SUDO_GID, SUDO_UID)
    csv_log.close()


# theme/icon paths for different desktop env
def theme_path(arg):

    # arg = (themes or icons or cursor)
    desktop_env_paths = {
        "gnome": {
            "theme_path": {
                "local": f"{HOME}/.local/share/themes",
                "global": f"/usr/share/themes",
            },
            "icon_path": {
                "local": f"{HOME}/.local/share/icons",
                "global": f"/usr/share/icons",
            },
            "cursor_path": {
                "local": f"{HOME}/.local/share/icons",
                "global": f"/usr/share/icons",
            },
        },
        "kde": {
            "theme_path": {
                "local": f"{HOME}/.local/share/plasma/desktoptheme/",
                "global": f"/usr/share/plasma/desktoptheme/",
            },
            "icon_path": {
                "local": f"{HOME}/.local/share/icons",
                "global": f"/usr/share/icons",
            },
            "cursor_path": {
                "local": f"{HOME}/.icons",
                "global": f"/usr/share/icons",
            },
        },
        "xfce": {
            "theme_path": {
                "local": f"{HOME}/.themes",
                "global": f"/usr/share/themes",
            },
            "icon_path": {
                "local": f"{HOME}/.icons",
                "global": f"/usr/share/icons",
            },
            "cursor_path": {
                "local": f"{HOME}/.icons",
                "global": f"/usr/share/icons",
            },
        },
    }

    for types in desktop_env_paths:

        if types in DESKTOP_SESSION:

            d = desktop_env_paths[types]

            if arg == "themes":
                if USER == "root":
                    return d["theme_path"]["global"]
                else:
                    return d["theme_path"]["local"]

            elif arg == "icons":
                if USER == "root":
                    return d["icon_path"]["global"]
                else:
                    return d["icon_path"]["local"]
            elif arg == "cursor":
                if USER == "root":
                    return d["cursor_path"]["global"]
                else:
                    return d["cursor_path"]["local"]


# print dirs
def listDir(path):

    if os.path.isdir(path):
        for dir in os.listdir(path):
            print(Fore.LIGHTGREEN_EX + dir + Fore.RESET)
    else:
        message.error("Given path is not a directory", stop_here=True)
        return False


def rmDir(themeName):

    path = [theme_path("icons"), theme_path("themes")]
    for p in path:
        if os.path.isdir(p + f"/{themeName}"):
            shutil.rmtree(p + f"/{themeName}")
            print(f"Removed: {themeName}")
            return True
    message.error("Theme not found", stop_here=True)
    return False


# user args
def interact():

    parser = argparse.ArgumentParser(
        description=f"""Gnome Theme Downloader -
            This script downloads - Icon, Shell and Cursor themes form https://www.gnome-look.org/, and automatically installs it,
            Just visit \"https://www.gnome-look.org/\" copy the url of the theme you want to install like the following example above showing,
            installing - Sweet theme.""",
        usage=f"{Fore.LIGHTGREEN_EX}gnomelooks [OPTIONS] [URL]{Fore.RESET}\n\n Example: gnomelooks -i 'https://www.gnome-look.org/p/1253385/'",
    )

    parser._optionals.title = "OPTIONS"

    parser.add_argument(
        "-i",
        metavar="[URL]",
        action="store",
        help="Install gnome - GTK/Shell ,Icon, Cursor theme.",
        type=str,
    )
    parser.add_argument(
        "-update",
        metavar="[Any string]",
        action="store",
        help="Update this tool",
        type=str,
    )
    parser.add_argument(
        "-ls",
        metavar="[gtk | icon]",
        action="store",
        help="list installed themes",
        type=str,
    )
    parser.add_argument(
        "-rm",
        metavar="theme name",
        action="store",
        help="remove any installed themes",
        type=str,
    )

    args = parser.parse_args()

    if args.i:
        url = args.i
        main(url)

    elif args.ls:
        if args.ls == "gtk":
            path = theme_path("themes")
        elif args.ls == "icon":
            path = theme_path("icons")
        else:
            message.error("Invalid argument", stop_here=True)
        listDir(path)

    elif args.rm:
        rmDir(args.rm)
    elif args.update:
        os.chdir(f"{HOME}/.gnomelooks")
        os.system("git pull origin master")
    else:
        parser.print_help()
        return False


# main
def main(url):

    # where files will  get downloaded
    temp_dir = f"/tmp/gnomelooks_temp_{USER}"

    print("Gnome-looks Theme-Downloader")

    v = [
        "www.opendesktop.org/",
        "www.pling.com/",
        "store.kde.org/",
        "www.gnome-look.org/",
        "www.xfce-look.org/",
    ]
    is_valid = False

    for u in v:
        if u in url:
            is_valid = True
            break

    if is_valid == False:
        message.error("Invalid url.", stop_here=True)
        return False

    product, looksData = scrapGnomeLooks(url)

    # detect install path

    if os.environ.get("TEST_THEME_INSTALLER") == "true":
        path = "./" + product["cat_title"]
    elif product["cat_title"] == "GTK3/4 Themes":
        path = theme_path("themes")
    elif product["cat_title"] == "Full Icon Themes":
        path = theme_path("icons")
    elif product["cat_title"] == "Cursors":
        path = theme_path("cursor")
    else:
        message.warning("Can't identify product category, using current path.")
        path = "."

    # create directory of theme path if not present
    if os.path.isdir(path) is False:
        os.makedirs(path)

    # print, scraped data

    # product
    print(
        Fore.GREEN
        + "\nTheme-Name: "
        + product["title"]
        + Fore.MAGENTA
        + f"\tLikes: {product['count_likes']}"
        + Fore.BLUE
        + f"\tCreator: {product['username']}\n"
        + Fore.RESET
    )

    # product description
    description = re.sub(
        r"\[\/?b|B\]|\[\/?url\]|\[\/?color.+\]|\[\/?code\]|\[\/?|\]",
        "",
        product["description"],
    )
    print(Fore.CYAN + "Description\n" + Fore.RESET + description)

    # product category
    print(Fore.YELLOW + f"\nCategory: {product['cat_title']}" + Fore.RESET)

    # scraped file json data
    printTable(looksData)

    print(f"Install Path: {path}")
    print(
        Fore.GREEN + "\nEnter Id to download & install Theme file:" + Fore.RESET,
        end=" ",
    )

    # Get / check valid input
    try:
        # g_id is custom id of gnome theme/icon
        g_ids = str(input())

    except ValueError:
        print("Enter valid Id")
        exit()

    # download to temp_dir
    def download(id, fileName):

        # create temp dir where tar files will be downloaded
        try:
            os.mkdir(temp_dir)
        except FileExistsError:
            pass

        themeUrl = unquote(looksData[id]["url"])

        message.info(f"Downloading {looksData[id]['name']} ....")
        file = requests.get(themeUrl)

        # download file through downloadlink,
        # and exit() if server status code other than 200.
        if file.status_code == 200:
            with open(f"{temp_dir}/{fileName}", "wb") as tar:
                tar.write(file.content)
            message.info(f"""Downloaded: {fileName} at {temp_dir}""")
        else:
            message.error("status_code {file.status_code}", stop_here=True)
            exit()

    def extract_theme(themeFile):
        # Extract ".tar" file to path, after download sucesses
        if ".tar" in themeFile:
            with tarfile.open(f"{temp_dir}/{themeFile}") as tar:
                tar.extractall(path=path)

                message.sucesses(f"""Extracted {themeFile}, at {path}""")
                log(themeFile, looksData[g_id]["updated_timestamp"], path, url)

        else:
            message.error("Not a tar file.", stop_here=True)
            return False

    for g_id in g_ids.split(","):
        g_id = int(g_id)
        themeFile = looksData[g_id]["name"]
        download(id=g_id, fileName=themeFile)
        extract_theme(themeFile)

    message.info("All set, Theme has been installed")
    print("Here is where you can see your installed theme")

    if DESKTOP_SESSION == "gnome":
        message.sucesses("Open: gnome-tweaks > Appearance > Applications")
    elif DESKTOP_SESSION in ["kde", "xfce"]:
        message.sucesses("Open: settings-manager > Appearance")


if __name__ == "__main__":
    interact()
