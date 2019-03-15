"""Script which uses beautiful soup and google's define to get the dictionary and thesaurus information of a word."""
import argparse
import requests
from bs4 import BeautifulSoup
import re


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


class Definition:
    """
    The main definition class. Parses the google search output for the important elements.
    """

    def __init__(self, soup):
        self.sentence = None
        self.phonetic = None
        self.forms = None
        self.fulldefs = None
        self.synolist = None
        self.antolist = None
        try:
            rawchunk = soup.find("div", id="ires")
        except:
            rawchunk = None

        if rawchunk:
            try:
                self.syllabic = rawchunk.find("span", attrs={"data-dobid": "hdw"}).text
            except AttributeError:
                self.syllabic = ""

            try:
                self.phonetic = rawchunk.find("span", class_="lr_dct_ph").text
            except AttributeError:
                self.phonetic = ""

            try:
                self.forms = [x.text for x in rawchunk.find_all("div", class_="xpdxpnd vk_gy")]
            except AttributeError:
                pass

            try:
                self.fulldefs = [i.text for i in rawchunk.find_all("div", attrs={"data-dobid": "dfn"})]
            except AttributeError:
                pass

            try:
                self.sentence = rawchunk.find("div", class_="lr_dct_more_blk xpdxpnd xpdnoxpnd vk_gy").text
            except AttributeError:
                pass

            try:
                thesrus = rawchunk.find_all("table", class_="vk_tbl vk_gy")
            except AttributeError:
                thesrus = None

            try:
                all_synonyms = [i.text.replace("synonyms:", "") for i in thesrus if "synonyms:" in i.text]
                self.synolist = [re.split(r"[;,]+", x) for x in all_synonyms]
            except AttributeError:
                pass

            try:
                all_antos = [i.text.replace("antonyms:", "") for i in thesrus if "antonyms:" in i.text]
                self.antolist = [re.split(r"[;,]+", x) for x in all_antos]
            except AttributeError:
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
    parser.add_argument(
        "--more",
        dest="more",
        action="store_true",
        required=False,
        default=False,
        help="Get more synonyms and antonyms.",
    )
    args = parser.parse_args()
    searchword = " ".join(args.search)
    defi = Definition(get_soup(searchword))
    if defi.syllabic:
        head = "%s . %s . %s" % (searchword, defi.syllabic, defi.phonetic)
        print(TerminalColours.HEADER + head + TerminalColours.ENDC)
        print(TerminalColours.OKGREEN + " - " + "\n - ".join(defi.fulldefs) + TerminalColours.ENDC)
        if defi.forms is not None:
            print("\n{}forms:{}".format(TerminalColours.HEADER, TerminalColours.ENDC))
            for row in defi.forms:
                form = [x.strip(" ") for x in row.split(";")]
                print("{} - {}{}".format(TerminalColours.OKGREEN, form[0], TerminalColours.ENDC))
                [print("{}   * {}{}".format(TerminalColours.OKGREEN, x, TerminalColours.ENDC)) for x in form[1:]]
        if defi.sentence is not None:
            print("\n{}usage:{}".format(TerminalColours.HEADER, TerminalColours.ENDC))
            print("{} {}{}".format(TerminalColours.OKGREEN, defi.sentence,TerminalColours.ENDC))
        if defi.synolist is not None:
            print("\n{}synonyms:{}".format(TerminalColours.HEADER, TerminalColours.ENDC))
            for i, row in enumerate(defi.synolist):
                if not args.more:
                    row = row[:5]
                print("{}- {}{}".format(TerminalColours.OKGREEN, ", ".join(row), TerminalColours.ENDC))
            # print(TerminalColours.OKGREEN + " " + ", ".join(defi.synolist) + TerminalColours.ENDC)
        if defi.antolist is not None:
            print("\n" + TerminalColours.HEADER + "antonyms:" + TerminalColours.ENDC)
            for i, row in enumerate(defi.antolist):
                if not args.more:
                    row = row[:5]
                print("{}- {}{}".format(TerminalColours.OKGREEN, ", ".join(row), TerminalColours.ENDC))
        print()
        if not args.more:
            print("Find more synonyms and antonyms by running with --more.")


if __name__ == "__main__":
    main()
