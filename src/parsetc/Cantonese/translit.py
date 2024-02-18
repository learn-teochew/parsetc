#!/usr/bin/env python3

import re
import json
import unicodedata

from importlib_resources import files
from lark import Transformer

# Load terminals and mergers data
TERMINALS = json.loads(
    files("parsetc").joinpath("Cantonese/terminals.json").read_text()
)
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

    def tone_citation(self, items):
        # Should only be one item
        return items[0][1]

    def tone_entering(self, items):
        # Should only be one item
        return items[0][1]

    # TODO metafunction to make functions here?
    def tone_1a(self, items):
        return "tone_1a", TERMINALS["tones"]["tone_1a"][self.system]

    def tone_1b(self, items):
        return "tone_1b", TERMINALS["tones"]["tone_1b"][self.system]

    def tone_2(self, items):
        return "tone_2", TERMINALS["tones"]["tone_2"][self.system]

    def tone_3(self, items):
        return "tone_3", TERMINALS["tones"]["tone_3"][self.system]

    def tone_4(self, items):
        return "tone_4", TERMINALS["tones"]["tone_4"][self.system]

    def tone_5(self, items):
        return "tone_5", TERMINALS["tones"]["tone_5"][self.system]

    def tone_6(self, items):
        return "tone_6", TERMINALS["tones"]["tone_6"][self.system]

    def tone_7(self, items):
        return "tone_7", TERMINALS["tones"]["tone_7"][self.system]

    def tone_8(self, items):
        return "tone_8", TERMINALS["tones"]["tone_8"][self.system]

    def tone_9(self, items):
        return "tone_9", TERMINALS["tones"]["tone_9"][self.system]

    def syllable_tone(self, items):
        return "".join([str_or_None(i) for i in items])

    def syllable_toneless(self, items):
        return "".join([str_or_None(i) for i in items])

    def word_sep(self, items):
        return "".join(items)

    def word_tone(self, items):
        return "".join(items)

    def _lookup_terminal(self, items, which="initial"):
        trdict = {
            term: TERMINALS[which][term][self.system]
            for term in TERMINALS[which]
            if self.system in TERMINALS[which][term]
        }
        for term in MERGERS[which]:
            if self.system in MERGERS[which][term]:
                merged_to = MERGERS[which][term][self.system]
                trdict[term] = TERMINALS[which][merged_to][self.system]
        return trdict[items[0].type]

    def initial(self, items):
        return Cantonese._lookup_terminal(self, items, "initial")

    def medial(self, items):
        return Cantonese._lookup_terminal(self, items, "medial")

    def codastop(self, items):
        return Cantonese._lookup_terminal(self, items, "codastop")

    def codanasal(self, items):
        return Cantonese._lookup_terminal(self, items, "codanasal")


class Jp(Cantonese):
    """Jyutping"""

    def __init__(self):
        self.system = "jp"


class Cpy(Cantonese):
    """Cantonese Pinyin"""

    def __init__(self):
        self.system = "cpy"


class Yale(Cantonese):
    """Yale Romanization"""

    def __init__(self):
        self.system = "yale"

    def syllable_toneless(self, items):
        raise Exception(
            "Cannot convert toneless syllables to Yale because of ambiguity"
        )

    def _lookup_terminal_withtype(self, items, which="initial"):
        trdict = {
            term: TERMINALS[which][term][self.system]
            for term in TERMINALS[which]
            if self.system in TERMINALS[which][term]
        }
        for term in MERGERS[which]:
            if self.system in MERGERS[which][term]:
                merged_to = MERGERS[which][term][self.system]
                trdict[term] = TERMINALS[which][merged_to][self.system]
        return which, trdict[items[0].type]

    def initial(self, items):
        return Yale._lookup_terminal_withtype(self, items, "initial")

    def medial(self, items):
        return Yale._lookup_terminal_withtype(self, items, "medial")

    def codastop(self, items):
        return Yale._lookup_terminal_withtype(self, items, "codastop")

    def codanasal(self, items):
        return Yale._lookup_terminal_withtype(self, items, "codanasal")

    def final(self, items):
        return "final", {i[0]: i[1] for i in items}

    def final_entering(self, items):
        return "final_entering", {i[0]: i[1] for i in items}

    def tone_citation(self, items):
        # Should only be one item
        return items[0]

    def tone_entering(self, items):
        # Should only be one item
        return items[0]

    def syllable_tone(self, items):
        trdict = {
            "tone_1a": "\u0304",
            "tone_1b": "\u0300",
            "tone_2": "\u0301",
            "tone_3": "",
            "tone_4": "\u0300",
            "tone_5": "\u0301",
            "tone_6": "",
            "tone_7": "\u0304",
            "tone_8": "",
            "tone_9": "",
        }
        # items is a list of: [initial] final tone_citation
        initial = items[0]  # first element, either tuple or None
        tone = items[-1][0]  # last element
        final_text = ""
        if items[1][0] == "final":
            final = items[1][1]
            if "medial" in final:
                final_text += final["medial"] + trdict[tone]
                if tone in ["tone_4", "tone_5", "tone_6"]:
                    final_text += "h"
                if "codanasal" in final:
                    final_text += final["codanasal"]
            else:  # codanasalnasal only
                final_text += final["codanasal"] + trdict[tone]
        elif items[1][0] == "final_entering":
            final = items[1][1]
            final_text += final["medial"] + trdict[tone]
            if tone == "tone_9":
                final_text += "h"
            final_text += final["codastop"]
        syllable_text = ""
        if initial is not None:
            syllable_text += initial[1]
        syllable_text += final_text
        return unicodedata.normalize("NFC", syllable_text)


# Available output formats for transformers
TRANSFORMER_DICT = {
    "jp": Jp(),
    "cpy": Cpy(),
    "yale": Yale(),
}
