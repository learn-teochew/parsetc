#!/usr/bin/env python3

import re
import json
import unicodedata

from importlib_resources import files
from lark import Transformer

# Load terminals and mergers data
TERMINALS = json.loads(files("parsetc").joinpath("Cantonese/terminals.json").read_text())
MERGERS = json.loads(files("parsetc").joinpath("Cantonese/mergers.json").read_text())


def str_or_None(s):
    """Convert to str or empty str if None

    Deal with null initial, which is encoded as None rather than a terminal
    """
    if s is None:
        return ""
    else:
        return str(s)

class Cantonese(Transformer):
    """Common to all Cantonese transformers unless overridden

    self.system is the key for the transcription system that is used to look up
    the data in the TERMINALS and MERGERS dicts
    """

    def __init__(self):
        self.system = None

    def start(self, items):
        return "".join(items)

    def sentence(self, items):
        return "".join(items)

    def sentence_tone(self, items):
        return "".join(items)

    def coda(self, items):
        return "".join([str(i) for i in items])

    def final(self, items):
        return "".join([str(i) for i in items])

    def final_entering(self, items):
        return "".join([str(i) for i in items])

    def tone(self, items):
        return "".join(items)

    def tone_citation(self, items):
        return "".join(items)

    def tone_entering(self, items):
        return "".join(items)

    # TODO metafunction to make functions here?
    def tone_1(self, items):
        return TERMINALS["tones"]["tone_1"][self.system]

    def tone_2(self, items):
        return TERMINALS["tones"]["tone_2"][self.system]

    def tone_3(self, items):
        return TERMINALS["tones"]["tone_3"][self.system]

    def tone_4(self, items):
        return TERMINALS["tones"]["tone_4"][self.system]

    def tone_5(self, items):
        return TERMINALS["tones"]["tone_5"][self.system]

    def tone_6(self, items):
        return TERMINALS["tones"]["tone_6"][self.system]

    def tone_7(self, items):
        return TERMINALS["tones"]["tone_7"][self.system]

    def tone_8(self, items):
        return TERMINALS["tones"]["tone_8"][self.system]

    def tone_9(self, items):
        return TERMINALS["tones"]["tone_9"][self.system]

    def syllable_tone(self, items):
        return "".join([str_or_None(i) for i in items])

    def syllable_toneless(self, items):
        return "".join([str_or_None(i) for i in items])

    def word_sep(self, items):
        return "".join(items)

    def word_tone(self, items):
        return "".join(items)

    def initial(self, items):
        trdict = {
            term: TERMINALS["initials"][term][self.system]
            for term in TERMINALS["initials"]
            if self.system in TERMINALS["initials"][term]
        }
        for term in MERGERS["initials"]:
            if self.system in MERGERS["initials"][term]:
                merged_to = MERGERS["initials"][term][self.system]
                trdict[term] = TERMINALS["initials"][merged_to][self.system]
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            term: TERMINALS["medials"][term][self.system]
            for term in TERMINALS["medials"]
            if self.system in TERMINALS["medials"][term]
        }
        for term in MERGERS["medials"]:
            if self.system in MERGERS["medials"][term]:
                merged_to = MERGERS["medials"][term][self.system]
                trdict[term] = TERMINALS["medials"][merged_to][self.system]
        return trdict[items[0].type]

    def codastops(self, items):
        trdict = {
            term: TERMINALS["codastops"][term][self.system]
            for term in TERMINALS["codastops"]
            if self.system in TERMINALS["codastops"][term]
        }
        for term in MERGERS["codastops"]:
            if self.system in MERGERS["codastops"][term]:
                merged_to = MERGERS["codastops"][term][self.system]
                trdict[term] = TERMINALS["codastops"][merged_to][self.system]
        return trdict[items[0].type]

    def codanasal(self, items):
        trdict = {
            term: TERMINALS["codanasals"][term][self.system]
            for term in TERMINALS["codanasals"]
            if self.system in TERMINALS["codanasals"][term]
        }
        for term in MERGERS["codanasals"]:
            if self.system in MERGERS["codanasals"][term]:
                merged_to = MERGERS["codanasals"][term][self.system]
                trdict[term] = TERMINALS["codanasals"][merged_to][self.system]
        return trdict[items[0].type]


class Jp(Cantonese):

    def __init__(self):
        self.system = "jp"

class Cpy(Cantonese):

    def __init__(self):
        self.system = "cpy"



# Available output formats for transformers
TRANSFORMER_DICT = {
    "jp": Jp(),
    "cpy": Cpy(),
}
