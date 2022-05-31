import re
import requests
import os
import shutil
import subprocess
import tkinter
import json
from tkinter import filedialog
from sys import platform
from notifypy import Notify


class TorrentFinder:
    def __init__(self) -> None:
        self.cacheDir = ".torrentCache"
        if not os.path.exists(self.cacheDir):
            os.mkdir(self.cacheDir)
        self.__results = list()
        self.__urlPrefix = "https://"
        self.__header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36"}
        with open("sitesInfo.json", 'r') as regFile:
            self.__sitesInfo = json.loads(regFile.read().rstrip())

    def __getElementList(self, site: str, name: str, page: str) -> list():
        return re.findall(self.__sitesInfo[site][name][0], page)

    def clearResults(self) -> None:
        self.__results.clear()

    def printOptions(self, numb: int) -> None:
        optionNumb = 1
        optionString = "({}) [{}] [{}] [{}] [S:{}] [L:{}] {}"
        for option in self.__results:
            if optionNumb > numb:
                break
            print(optionString.format(optionNumb, option[0],
                  option[6], option[5], option[3], option[4], option[2]))
            optionNumb += 1

    def chooseOption(self, numb: int) -> str:
        optionSize = min(len(self.__results), numb)
        optionString = "Choose a torrent to watch [1-{}]: ".format(optionSize)
        choice = -1
        while choice > optionSize or choice < 1:
            choice = input(optionString)
            if choice.isnumeric():
                choice = int(choice)
            else: 
                choice = -1
        magnetPage = requests.get(
            self.__results[choice-1][1], headers=self.__header)
        magnetLink = re.search(
            self.__sitesInfo[self.__results[choice-1][0]]["magnet"][0], magnetPage.text)
        return magnetLink[1]

    def fetchInfo(self, name: str) -> bool:
        name = name.replace(' ', '%20')
        for site, regex in self.__sitesInfo.items():
            for query in regex["query"]:
                url = self.__urlPrefix + site + \
                    self.__sitesInfo[site]["query"][0].format(name)
                try:
                    page = requests.get(url, headers=self.__header)
                except:
                    continue
                page = page.text
                names = self.__getElementList(site, "name", page)
                if not len(names):
                    continue
                links = self.__getElementList(site, "link", page)
                seeders = self.__getElementList(site, "seeders", page)
                leechers = self.__getElementList(site, "leechers", page)
                dates = self.__getElementList(site, "time", page)
                sizes = self.__getElementList(site, "size", page)
                for cnt in range(len(names)):
                    removeWords = ["<strong class=\"red\">", "</strong>"]
                    for word in removeWords:
                        if word in names[cnt]:
                            names[cnt] = names[cnt].replace(word, '')
                    names[cnt] = names[cnt].replace('-', ' ')
                    if type(dates[cnt]) is not str:
                        dates[cnt] = " ".join(x for x in dates[cnt]) + " ago"
                    self.__results.append([site, self.__urlPrefix + site + links[cnt], names[cnt], int(
                        seeders[cnt]), int(leechers[cnt]), dates[cnt], sizes[cnt]])
        if not len(self.__results):
            print("No magnet links found!")
            return False
        self.__results.sort(key=lambda res: res[3], reverse=True)
        return True

    def cleanup(self) -> None:
        shutil.rmtree(self.cacheDir, ignore_errors=True)


def clearScreen() -> None:
    subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)


def sendNotification(message: str) -> None:
    notification = Notify()
    if os.path.isfile("./proflix.png"):
        notification.icon = "./proflix.png"
    notification.title = "Proflix notification"
    notification.message = message
    notification.send(block=False)


def selectSubFile() -> str:
    subPath = filedialog.askopenfilename()
    if type(subPath) is str and subPath != '':
        return subPath
    else:
        choice = input("Did not specify any file. Do you want to try again?(Y/n): ").lower()
        if choice == 'y' or choice == '':
            return selectSubFile()
        else:
            return ''


def selectDir() -> str:
    selectedDir = filedialog.askdirectory()
    if type(selectedDir) is str and selectedDir != '':
        return selectedDir
    else:
        choice = input("Did not specify any download directory. Do you want to try again?(Y/n): ").lower()
        if choice == 'y' or choice == '':
            return selectDir()
        else:
            return ''


def chooseApp() -> str:
    print("What do you want to do?\n  1) Download media\n  2) Stream media")
    optionString = "Choose an option [1-2]: "
    option  = -1
    while option not in range(1,3):
            option = input(optionString)
            if option.isnumeric():
                option = int(option)
            else: 
                option = -1
    return option


def main() -> None:
    finder = TorrentFinder()
    clearScreen()
    appOption = chooseApp()
    clearScreen()
    if appOption == 1:
        print("Select download directory:")
        shellCommand = "webtorrent download \"{}\""
        downloadDir = selectDir()
        if len(downloadDir):
            shellCommand += " -o {} "
    else:
        shellCommand = "webtorrent \"{}\" -o {} --mpv"
    name = input("🧲 Media to search: ")
    optionsNumb = ''
    while not optionsNumb.isnumeric() or int(optionsNumb) < 1:
        optionsNumb = input("Max number of results: ")
    optionsNumb = int(optionsNumb)
    clearScreen()
    if not finder.fetchInfo(name):
        choice = input("Want to continue? (Y/n): ").lower()
        if choice == 'y' or choice == '':
            finder.clearResults()
            clearScreen()
            main()
        else:
            return
    finder.printOptions(optionsNumb)
    magnetLink = finder.chooseOption(optionsNumb)
    if appOption == 1:
        shellCommand = shellCommand.format(magnetLink, downloadDir)
    else:
        shellCommand = shellCommand.format(magnetLink, finder.cacheDir)
        choice = input("Do you want to load any subtitles file?(Y/n): ").lower()
        if choice == 'y' or choice == '':
            tkinter.Tk().withdraw()
            subPath = selectSubFile()    
            if subPath != '':
                shellCommand += " -t {}".format(subPath)
        sendNotification("🎥 Enjoy Watching ☺️")
    subprocess.call(shellCommand, shell=True)
    
    if appOption == 1:
        sendNotification("Download complete!💯")

    finder.cleanup()


if __name__ == "__main__":
    main()
