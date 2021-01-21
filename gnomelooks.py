#! /usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import json, csv
import os, subprocess, shutil
import argparse
from colorama import Fore

USER = os.environ.get("USER")
HOME = os.environ.get("HOME")

def scrapGnomeLooks(url):

    gnome_looks_page = requests.get(url)
    if gnome_looks_page.status_code == 404:
        print(Fore.RED+"Error: Page responded 404 (File not found)"+Fore.RESET)
        exit()
    
    soup = BeautifulSoup(gnome_looks_page.text,'lxml')
    
    # where a variable contain json data of theme-files
    try:
        apiData = soup.select_one('#od-body > script:nth-child(20)').string
        re.search(r"filesJson = ", apiData)
    except TypeError:
        # if api-json is not present at jspath, bruteforce for jspath
        script_child=[15,16,17,18,19,20,21,22,23,24,25]
        for blind_id in script_child:
            try:
                apiData = soup.select_one(f'#od-body > script:nth-child({blind_id})').string
                if re.search(r"filesJson = \[", apiData):
                    break
            except:
                continue
    
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
        # print(f"""{'':<4}| {'':<{max_len_filename}}| {'':<10} | {'':<10}| {'':<6}   |""")
    
    print( "-" * (4+max_len_filename+10+10+8 + 11) )


# save csv log of downloaded files
def log(filename, date, path, url):
    
    logFile = f"{HOME}/.gnomelooks_log.csv"
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


def theme_path(arg):
    # themes
    # icons
    if USER == "root":
        path = f"/usr/share/{arg}"
    else:
        path = f"""{HOME}/.local/share/{arg}"""
    return path

# print dirs
def listDir(path):

    if os.path.isdir(path):
        for dir in os.listdir(path):
            print(Fore.LIGHTGREEN_EX + dir + Fore.RESET)
    else:
        print(Fore.RED + "Error: Given path is not a directory" + Fore.RESET)
        return False

def rmDir(themeName):
    
    path = [theme_path("icons"), theme_path("themes")]
    for p in path:
        if os.path.isdir(p + f"/{themeName}"):
            shutil.rmtree(p + f"/{themeName}")
            print(f"Removed: {themeName}")
            return True
    print(Fore.RED+'Theme not found'+Fore.RESET)
    return False

# print list themes
def l(arg):
    
    # list directory of gtk/icon themes
    if arg == 'gtk':
        path = theme_path("themes")
    elif arg == 'icon':
        path = theme_path("icons")
    else:
        print(Fore.RED+'Invalid argument'+Fore.RESET)
        exit()
    return path

# user args
def interact():

    parser = argparse.ArgumentParser(
        
        description = f"""Gnome Theme Downloader -
            This script downloads - Icon, Shell and Cursor themes form https://www.gnome-look.org/, and automatically installs it,
            Just visit \"https://www.gnome-look.org/\" copy the url of the theme you want to install like the following example above showing,
            installing - Sweet theme.""",

        usage=f"{Fore.LIGHTGREEN_EX}gnomelooks [OPTIONS] [URL]{Fore.RESET}\n\n Example: gnomelooks -i \'https://www.gnome-look.org/p/1253385/\'"
    )

    parser._optionals.title = "OPTIONS"
    parser.add_argument("-i", metavar="[URL]", action="store", help="Install gnome - GTK/Shell ,Icon, Cursor theme.", type=str,)
    parser.add_argument("-ls", metavar="[gtk | icon]", action="store", help="list installed themes", type=str)
    parser.add_argument("-rm", metavar="theme name", action="store", help="remove any installed themes", type=str)

    args  = parser.parse_args()

    if args.i:
        url = args.i
        main(url)
    
    elif args.ls:
        path = l(args.ls)
        listDir(path)
    
    elif args.rm:
        rmDir(args.rm)
    
    else:
        parser.print_help()
        return False

# main
def main(url):
    
    # where files will  get downloaded
    temp_dir=f"/tmp/gnomelooks_temp_{USER}"

    print("Gnome-looks Theme-Downloader")
    
    # is valid url input ?
    if "https://www.gnome-look.org/" not in url and "https://www.pling.com/" not in url:
        print(Fore.RED +"Invalid URL." + Fore.RESET)
        return False

    product, looksData = scrapGnomeLooks(url)

    # detect install path

    if product['cat_title'] == "GTK3 Themes":
        path = theme_path("themes")
    elif product['cat_title'] == "Full Icon Themes":
        path = theme_path("icons")
    elif product['cat_title'] == "Cursors":
        path = theme_path("icons")
    else:
        path = '.'

    # create directory of theme path if not present
    
    if os.path.isdir(path) is False:
        os.makedirs(path)

    # print, scraped data
    
    # product
    print(Fore.GREEN + '\nTheme-Name: '+ product["title"] + Fore.MAGENTA + f"\tLikes: {product['count_likes']}" + Fore.BLUE + f"\tCreator: {product['username']}\n" + Fore.RESET )

    # product description
    description = re.sub(r"\[\/?b|B\]|\[\/?url\]|\[\/?color.+\]|\[\/?code\]|\[\/?|\]", "", product["description"])
    print(Fore.CYAN+ "Description\n" + Fore.RESET + description)

    # product category
    print(Fore.YELLOW + f"\nCategory: {product['cat_title']}" + Fore.RESET)
        
    # scraped file json data
    printTable(looksData)

    print(Fore.GREEN + "\nEnter Id to download & install Theme file:" + Fore.RESET)
    
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

        print(f"Downloading {looksData[g_id]['name']} ....")
        file = requests.get(themeUrl)
        
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
    
    print(Fore.GREEN + "\nAll set, Theme has been installed\nHere is where you can see your installed theme")
    print(Fore.LIGHTMAGENTA_EX + "Open: gnome-tweaks > Appearance > Applications" + Fore.RESET)


if __name__ == '__main__':
    interact()
