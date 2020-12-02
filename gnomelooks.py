#! /usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import json, csv
import os, subprocess
import argparse
from colorama import Fore


def main(url, path):
    
    # where files will  get downloaded
    temp_dir="/tmp/gnomelooks_temp"

    print("Gnome-looks Theme-Downloader")
    
    # is valid url input ?
    if "https://www.gnome-look.org/" not in url:
        print(Fore.RED +"Invalid URL." + Fore.RESET)
        return False
    
    # create directory of theme path if not present
    if os.path.isdir(path) is False:
        os.makedirs(path)

    title, looksData = scrapGnomeLooks(url)

    # title
    print(Fore.GREEN + '\nTheme-Name: '+ title + Fore.RESET)
    # print, scraped data
    printTable(looksData)

    print(Fore.GREEN + "\nEnter Id to download file:" + Fore.RESET)
    
    # Get / check valid input
    try:
        # g_id is custom id of gnome theme/icon
        g_id = int(input())

        if g_id > len(looksData)-1:
            print(Fore.RED + f'Error: Id out of range, enter a valid Id\nRange of Id is between 0-{len(looksData)-1}' + Fore.RESET)
            return False
        else:
            themeFile = looksData[g_id]["name"]
    
    except ValueError:
        print("Enter Id , of integer type")
        exit()
    
    # download to temp_dir
    def download(g_id):

        # create temp dir where tar files will be downloaded
        try:
            os.mkdir(temp_dir)
        except FileExistsError:
            pass
        
        themeUrl = unquote(looksData[g_id]["url"])

        file = requests.get(themeUrl)
        print(f"Downloading {looksData[g_id]['name']} ....")
        
        # download file through downloadlink, 
        # and exit() if server status code other than 200.
        if file.status_code == 200:
            with open(f'{temp_dir}/{themeFile}','wb') as tar:
                tar.write(file.content)
            print(f"""Downloaded: {themeFile} at {temp_dir}""")
        else:
            print(f"Error: status_code {file.status_code}")
            exit()
    
    
    download(g_id)
    
    # Extract ".tar" file to path, after download sucesses
    if ".tar" in themeFile:
        tarExtract(f'{temp_dir}/{themeFile}', path)
        print(f"""Extracted {themeFile}, at {path}""")
        
        log(themeFile, looksData[g_id]["updated_timestamp"], path, url)

    else:
        print("Error: Not a tar file.")
        return False


def scrapGnomeLooks(url):

    soup = BeautifulSoup(requests.get(url).text,'lxml')
    
    # where a variable contain json data of theme-files
    script_tag_19 = soup.select_one('#od-body > script:nth-child(19)').string
    title = soup.select("#product-header-title > a")[0].text.strip()

    # collect filesJson -> list having json data in it
    pattern = r"filesJson = (\[.*\])"
    data = re.search(pattern, script_tag_19)[1]
    
    # collect active files and ignore archived ones.
    def collect_active(jsonList):
        
        active = []
        for i in range(len(jsonList)):
            if jsonList[i]["active"] == "1":
                active.append(jsonList[i])
        return active

    return title, collect_active(json.loads(data))

# print scraped data in form of tables 
def printTable(activeList):

    # get max_len_filename, to calc the area needed to printTable()
    len_filename = []
    for  i in range(len(activeList)):
        len_filename.append(len(activeList[i]['name']))
    max_len_filename = max(len_filename)+1

    print( Fore.CYAN  + f"""\n{"Id":<4}| {"Filename":<{max_len_filename}}| {"Date":<10} | {"Downloads":<10}| {"Size":<8} |""" + Fore.RESET)
    print( "-" * (4+max_len_filename+10+10+8 + 11) )
    
    for  i in range(len(activeList)):
        
        filename = activeList[i]['name']
        updated_timestamp = activeList[i]['updated_timestamp'][:10]
        downloaded_count = activeList[i]['downloaded_count']
        sizeMB = round( int(activeList[i]['size']) / 1000000 , 3)

        print(f"""{i:<4}| {filename:<{max_len_filename}}| {updated_timestamp:<10} | {downloaded_count:<10}| {sizeMB:<6}MB |""")
    
    print( "-" * (4+max_len_filename+10+10+8 + 11) )



# save csv log of downloaded files
def log(filename, date, path, url):
    
    logFile = f"{os.environ.get('HOME')}/.gnomelooks_log.csv"
    logFile_exist = os.path.isfile(logFile)

    with open(logFile,'a+') as csv_log:
        fieldname = ["FILENAME", "DATE", "PATH", "PAGE"]
        writer = csv.DictWriter(csv_log, fieldnames=fieldname)

        if not logFile_exist:
            writer.writeheader()

        writer.writerow({"FILENAME": filename, "DATE": date, "PATH": path, "PAGE": url})


# extract tar files
def tarExtract(filename, directory):

    if os.path.isdir(directory) is False:
        os.makedirs(directory)

    command = f"tar -xf {filename} --directory {directory}"
    subprocess.Popen(command.split(), stdout=subprocess.PIPE)


def gtk_theme_path():

    if os.environ.get("USER") == "root":
        path = "/usr/share/themes"
    else:
        path = f"""{os.environ.get("HOME")}/.local/share/themes"""
    
    return path


def icon_theme_path():

    if os.environ.get("USER") == "root":
        path = "/usr/share/icons"
    else:
        path = f"""{os.environ.get("HOME")}/.local/share/icons"""
    return path


def cursor_theme_path():

    # cursor and icon themes are located at same path
    if os.environ.get("USER") == "root":
        path = "/usr/share/icons"
    else:
        path = f"""{os.environ.get("HOME")}/.local/share/icons"""
    return path

# print dirs
def listDir(path):

    if os.path.isdir(path):
        for dir in os.listdir(path):
            print(Fore.LIGHTGREEN_EX + dir + Fore.RESET)
    else:
        print(Fore.RED + "Error: Given path is not a directory" + Fore.RESET)
        return False


# print list themes
def l(arg):
    
    # list directory of gtk/icon themes
    if arg == 'gtk':
        path = gtk_theme_path()
    if arg == 'icon':
        path = icon_theme_path()
    
    return listDir(path)

# user args
def interact():

    parser = argparse.ArgumentParser(
        
        description = f"""Gnome Theme Downloader -
            This script downloads - Icon, Shell and Cursor themes form https://www.gnome-look.org/, and automatically installs it,
            Just visit \"https://www.gnome-look.org/\" copy the url of the theme you want to install like the following example above showing,
            installing - Sweet theme.""",

        usage=f"{Fore.LIGHTGREEN_EX}gnomelooks --gtk 'https://www.gnome-look.org/p/1253385/'{Fore.RESET}"
    )

    parser._optionals.title = "OPTIONS"
    parser.add_argument("--gtk", metavar="[URL]", action="store", help="download and install gnome gtk/shell theme.", type=str,)
    parser.add_argument("--icon", metavar="[URL]", action="store", help="download and install gnome icon theme.", type=str)
    parser.add_argument("--cursor", metavar="[URL]", action="store", help="download and install gnome cursor theme.", type=str)
    parser.add_argument("-ls", metavar="gtk | icon", action="store", help="List installed themes", type=str)

    args  = parser.parse_args()


    if args.gtk:
        url = args.gtk
        path = gtk_theme_path()
        
    elif args.icon:
        url = args.icon
        path = icon_theme_path()
    
    elif args.cursor:
        url = args.cursor
        path = cursor_theme_path()  
    
    elif args.ls:
        l(args.ls)
    
    else:
        parser.print_help()
        return False
    
    if 'path' in locals():
        main(url, path)


if __name__ == '__main__':
    interact()
