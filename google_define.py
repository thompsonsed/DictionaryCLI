"""Script which uses beautiful soup and google's define to get the dictionary and thesaurus information of a word."""
import argparse
import requests
from bs4 import BeautifulSoup


def get_soup(searchword):
    """
    Searches google for the given word.

    :param str searchword: the word to search for.
    :return: theit st
    """
    base = "https://www.google.com/search"
    params = {"q": "define:%s" % searchword}
    headers = {"User-Agent": "Firefox 18.3"}
    req = requests.get(base, params=params, headers=headers)
    soup = BeautifulSoup(req.text, "html5lib")
    return soup


class definition:
    """
    The main definition class. Parses the google search output for the important elements.
    """

    def __init__(self, soup):
        try:
            rawchunk = soup.find("div", id="ires")
        except:
            rawchunk = None

        if rawchunk:
            try:
                self.syllabic = rawchunk.find("span", attrs={"data-dobid": "hdw"}).text
            except:
                self.syllabic = ""

            try:
                self.phonetic = rawchunk.find("span", class_="lr_dct_ph").text
            except:
                self.phonetic = ""

            try:
                self.forms = rawchunk.find("div", class_="xpdxpnd vk_gy").text
            except:
                pass

            try:
                self.fulldefs = [i.text for i in rawchunk.find_all("div", attrs={"data-dobid": "dfn"})]
            except:
                pass

            try:
                self.sentence = rawchunk.find("div", class_="lr_dct_more_blk xpdxpnd xpdnoxpnd vk_gy").text
            except:
                pass

            try:
                thesrus = rawchunk.find_all("table", class_="vk_tbl vk_gy")
            except:
                pass

            try:
                self.synolist = [i.text for i in thesrus[0].find_all("a")]
            except:
                pass

            try:
                self.antolist = [i.text for i in thesrus[1].find_all("a")]
            except:
                pass

    def __repr__(self):
        return __name__


def main():
    """
    Runs the main loop, searching google for the definition and printing the result out with colouring.
    """

    class TerminalColours:
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"

    parser = argparse.ArgumentParser()
    parser.add_argument("search", nargs="+", help="type the word you want to search here")
    args = parser.parse_args()
    searchword = " ".join(args.search)
    defi = definition(get_soup(searchword))
    if defi.syllabic:
        head = "%s . %s . %s" % (searchword, defi.syllabic, defi.phonetic)
        print(TerminalColours.HEADER + head + TerminalColours.ENDC)
        print(TerminalColours.OKGREEN + " - " + "\n - ".join(defi.fulldefs) + TerminalColours.ENDC)
        if hasattr(defi, "forms"):
            print("\n" + TerminalColours.HEADER + "forms:" + TerminalColours.ENDC)
            print(TerminalColours.OKGREEN + " - " + "\n - ".join(defi.forms.split(";")) + TerminalColours.ENDC)
        if hasattr(defi, "sentence"):
            print("\n" + TerminalColours.HEADER + "usage:" + TerminalColours.ENDC)
            print(TerminalColours.OKGREEN + " " + defi.sentence + TerminalColours.ENDC)
        if hasattr(defi, "synolist"):
            print("\n" + TerminalColours.HEADER + "synonyms:" + TerminalColours.ENDC)
            print(TerminalColours.OKGREEN + " " + ", ".join(defi.synolist) + TerminalColours.ENDC)
        if hasattr(defi, "antolist"):
            print("\n" + TerminalColours.HEADER + "antonyms:" + TerminalColours.ENDC)
            print(TerminalColours.OKGREEN + " " + ", ".join(defi.antolist) + TerminalColours.ENDC)
        print()


if __name__ == "__main__":
    main()
