import re, requests, os
from sys import platform

class Data:
    def __init__(self) -> None:
        self.cacheDir = ".torrentCache"
        if platform.lower() == "windows":
            os.system("rmdir -r .\{}\ ".format(self.cacheDir))
            os.system("mkdir {}".format(self.cacheDir))
        else:
            os.system("rm -r {}".format(self.cacheDir))
            os.system("mkdir {}".format(self.cacheDir))
        self.__results = list()
        self.__urlPrefix = "https://"
        self.__header = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36"}
        self.__sitesInfo = {
            "1337x.to" : {
                "query" : "/sort-search/{}/seeders/desc/1/",
                "name" : "<a href=\"/torrent/\d+/(.+)/\">.*</a>",
                "link" : "<a href=\"(/torrent/.+)\">.*</a>",
                "seeders" : "<td class=\"coll-2 seeds\">(\d+)</td>",
                "leechers" : "<td class=\"coll-3 leeches\">(\d+)</td>",
                "time" : "<td class=\"coll-date\">(.+)</td>",
                "size" : "<td class=\"coll-4 size.*\">(.+)<span.*</td>",
                "magnet" : "(magnet:.+)\".on"
            }
        }

    def __getElementList(self, site : str, name : str, page : str) -> list():
        return re.findall(self.__sitesInfo[site][name], page)

    def printOptions(self) -> None:
        optionNumb = 1
        optionString = "({}) [{}] [{}] [S:{}] [L:{}] {}"
        for option in self.__results:
            print(optionString.format(optionNumb, option[6], option[5], option[3], option[4], option[2]))
            optionNumb += 1
    
    def chooseOption(self) -> None:
        optionSize = len(self.__results)
        optionString = "Choose a torrent to watch[1-{}]:".format(optionSize)
        choice = -1
        while choice > optionSize or choice < 1:
            choice = int(input(optionString))
        magnetPage = requests.get(self.__results[choice-1][1], headers=self.__header)
        magnetLink = re.search(self.__sitesInfo[self.__results[choice-1][0]]["magnet"], magnetPage.text)
        return magnetLink[1]

    def fetchInfo(self, name : str) -> bool:
        name = name.replace(' ', '+')
        for site in self.__sitesInfo:
            url = self.__urlPrefix + site + self.__sitesInfo[site]["query"].format(name)
            try:
                page = requests.get(url, headers=self.__header)
            except:
                continue
            page = page.text
            names =  self.__getElementList(site, "name", page)
            if not len(names):
                print("No magnet links found!")
                return False
            links = self.__getElementList(site, "link", page)
            seeders = self.__getElementList(site, "seeders", page)
            leechers = self.__getElementList(site, "leechers", page)
            dates = self.__getElementList(site, "time", page)
            sizes = self.__getElementList(site, "size", page)
            for cnt in range(len(names)):
                self.__results.append([site, self.__urlPrefix + site + links[cnt], names[cnt], seeders[cnt], leechers[cnt], dates[cnt], sizes[cnt]])
            return True

def clearScreen() -> None:
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    name = input("🧲Media to search:")
    clearScreen()
    if not data.fetchInfo(name):
        choice = input("Want to continue?(Y/n)").lower()
        if choice == 'y' or choice == '':
            data.results.clear()
            Data.clearScreen()
            main()
        else:
            return
    data.printOptions()
    magnetLink = data.chooseOption()
    os.system("notify-send \"🎥 Enjoy Watching ☺️ \" -i \"NONE\"")
    os.system("webtorrent \"{}\" -o \"{}\" --mpv".format(magnetLink, data.cacheDir))

if __name__ == "__main__":
    data = Data()
    clearScreen()
    main()

#"torrentgalaxy.to" : {
#                "query" : "/torrents.php?search={}&lang=0&nox=2&sort=seeders&order=desc",
#                "name" : "<.*a.*class.*=.*\".*txlight.*\".*title.*=.*\"(.+)\".*href.*=.*\".*\".*>.*<.*/.*a.*>",
#                "link" : "<.*a.*class.*=.*\".*txlight.*\".*title.*=.*\".+\".*href.*=.*\"(.+)\".*>.*<.*/.*a.*>",
#                "seeders" : "<.*span.*title.*=.*\".*Seeders.*/.*Leechers.*\".*>.*<.*font.*color.*=.*\".*green.*\">.*<.*b.*>(.+)<.*b.*>.*<.*/.*font.*>",
#                "leechers" : "<.*span.*title.*=.*\".*Seeders.*/.*Leechers.*\".*>.*<.*font.*color.*=.*\".*#ff0000.*\">.*<.*b.*>(.+)<.*b.*>.*<.*/.*font.*>",
#                "time" : "<.*div.*class.*=.*\".*tgxtablecell.*collapsehide.*rounded.*txlight.*\".*style.*=.*\".*text-align.*:.*right.*\".*>.*<.*small.*>(.+)<.*/.*small.*>.*<.*/.*div.*>",
#                "size" : "<.*span.*class.*=.*\".*badge.*badge-secondary.*txlight\".*style.*=.*\".*border-radius.*:.*4px.*;.*\".*>(.+)<.*/.*span.*>"
#            } 
#"rarbg.to" : {
#   "query" : "/search/1/?search={}&order=seeders&by=DESC"
# }