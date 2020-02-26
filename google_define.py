"""Script which uses google's define to get the dictionary and thesaurus information of a word."""
import argparse
import json

import requests


class TerminalColours:
    """Define the colours for printing to the terminal."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


class Interpretation:
    def __init__(self, keyword, more, word, phonetic, meanings):
        """Contains a single interpretation of the a particular word"""
        self.keyword = keyword
        self.more = more
        self.word = word
        self.phonetic = phonetic
        self.meanings = meanings

    def output(self):
        """Outputs the stored word, meanings and phonetics to the terminal."""
        head = "{} . {} . {}".format(self.keyword, self.word, self.phonetic)
        print("{}{}{}".format(TerminalColours.HEADER, head, TerminalColours.ENDC))
        for k, type in self.meanings.items():
            print("{}{}{}".format(TerminalColours.HEADER, k, TerminalColours.ENDC))
            for i, meaning in enumerate(type):
                print()
                # Only output the first 2 definitions for each group, unless more is provided.
                if i > 1 and not self.more:
                    break
                for base_colour, group in [
                    (TerminalColours.OKGREEN, "definition"),
                    (TerminalColours.OKBLUE, "synonyms"),
                    (TerminalColours.OKBLUE, "antonyms"),
                ]:
                    if group in meaning.keys():
                        vals = meaning.get(group, "")
                        if isinstance(vals, list):
                            # Just output the first 5 arguments
                            if not self.more:
                                vals = vals[:5]
                            vals = ", ".join(vals)
                        print("{} - {}: {}{}".format(base_colour, group, vals, TerminalColours.ENDC))
            print()


class DictionarySearch:
    """The main definition class. Parses the google search output for the important elements."""

    def __init__(self, keyword, more=False):
        self.text = None
        self.keyword = keyword
        self.more = more
        self.interpretations = []

    def get_request(self):
        """
        Gets a request from an unofficial google dictionary api of the set keyword.
        """
        try:
            req = requests.get(f"https://api.dictionaryapi.dev/api/v1/entries/en/{str(self.keyword)}", timeout=10)
            if req.status_code == requests.codes.ok:
                self.text = req.text
                req.close()
            else:
                raise requests.exceptions.RequestException("Request return code not OK.")
        except requests.exceptions.RequestException:
            for site in ["https://mydictionaryapi.appspot.com/", "https://googledictionaryapi.eu-gb.mybluemix.net/"]:
                try:
                    req = requests.get(site, params={"define": str(self.keyword)}, timeout=10)
                    if req.status_code == requests.codes.ok:
                        self.text = req.text
                        req.close()
                        break
                except requests.exceptions.RequestException:
                    pass
        if self.text is None:
            raise IOError("Could not get query form unofficial google dictionary api.")

    def parse_text(self):
        """Parses the text into json."""
        j = json.loads(self.text)
        if not isinstance(j, list):
            j = [j]
        for each in j:
            self.interpretations.append(
                Interpretation(
                    self.keyword,
                    self.more,
                    each.get("word", self.keyword),
                    each.get("phonetic", ""),
                    each.get("meaning"),
                )
            )

    def output(self):
        """Write all interpretations to the console."""
        for interpretation in self.interpretations:
            interpretation.output()

    def __repr__(self):
        return __name__


def main():
    """
    Runs the main loop, searching google for the definition and printing the result out with colouring.
    """

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
    d = DictionarySearch(searchword, args.more)
    d.get_request()
    d.parse_text()
    d.output()
    if not args.more:
        print("Find more synonyms and antonyms by running with --more.")


if __name__ == "__main__":
    main()
