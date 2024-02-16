#!/usr/bin/env python3

import re
import json
import unicodedata

from importlib_resources import files
from lark import Transformer

# Load terminals and mergers data
TERMINALS = json.loads(files("parsetc").joinpath("terminals.json").read_text())
MERGERS = json.loads(files("parsetc").joinpath("mergers.json").read_text())


class Tctransformer(Transformer):
    """Common to all transformers unless overridden

    self.system is the key for the transcription system that is used to look up
    the terminals and mergers data.
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

    def syllable_tone(self, items):
        return "".join([str(i) for i in items])

    def syllable_toneless(self, items):
        return "".join([str(i) for i in items])

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
        # initials that have merged in modern Teochew
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


class Gdpi(Tctransformer):
    """Convert Teochew pengim parse tree to Gengdang Pêng'im"""

    def __init__(self):
        self.system = "gdpi"

    def NASAL(self, value):
        return "n"

    def tone(self, items):
        if len(items) == 1:
            return str(items[0])
        elif len(items) == 2:
            return str(items[0]) + "(" + str(items[1]) + ")"
        else:
            return ""


class Ggnn(Tctransformer):
    """Convert Teochew pengim parse tree to Gaginang Peng'im"""

    def __init__(self):
        self.system = "ggnn"

    def NASAL(self, value):
        return "ñ"

    def tone(self, items):
        if len(items) == 1:
            return str(items[0])
        elif len(items) == 2:
            return str(items[0]) + "(" + str(items[1]) + ")"
        else:
            return ""


class Tlo(Tctransformer):
    """Convert Teochew pengim parse tree to Tie-lo"""

    def __init__(self):
        self.system = "tlo"

    def NASAL(self, value):
        return "nn"

    def SYLLABLE_SEP(self, value):
        # Change all syllable separators to hyphens
        return "-"

    def tone(self, items):
        # Only return the citation tone
        return str(items[0])

    def syllable_tone(self, items):
        # Tie-lo is less straightforward because it marks
        # tones with diacritics
        trdict = {
            "1": "",
            "2": "\u0301",
            "3": "\u0300",
            "4": "",
            "5": "\u0302",
            "6": "\u0306",
            "7": "\u0304",
            "8": "\u0302",
            "0": "",
        }
        syllab = "".join(items[:-1])  # syllable without tone
        tone = items[-1]
        firstvowel = re.search(r"[aeiou]", syllab)
        if firstvowel:
            # put tone mark on first vowel letter
            inspos = firstvowel.span()[1]
        else:
            # no vowel in syllable, put on nasal codas n or m, n comes first
            firstnasal = re.search(r"[nm]", syllab)
            inspos = firstnasal.span()[1]
        syllab = syllab[0:inspos] + trdict[tone] + syllab[inspos:]
        syllab = unicodedata.normalize("NFC", syllab)
        return syllab

    def word_sep(self, items):
        # replace all syllable separators with hyphens
        # and separate syllables with hyphens if no
        # syllable separator is present
        return "-".join([i for i in items if i != "-"])

    def word_tone(self, items):
        return "-".join([i for i in items if i != "-"])


class Duffus(Tctransformer):
    """Convert Teochew pengim parse tree to Duffus system"""

    def __init__(self):
        self.system = "duffus"

    def NASAL(self, value):
        return "\u207f"

    def SYLLABLE_SEP(self, value):
        # Change all syllable separators to hyphens
        return "-"

    def tone(self, items):
        # Only return the citation tone
        return str(items[0])

    def syllable_tone(self, items):
        trdict = {
            "1": "",
            "2": "\u0301",
            "3": "\u0300",
            "4": "",
            "5": "\u0302",
            "6": "\u0303",
            "7": "\u0304",
            "8": "\u0307",
            "0": "",
        }
        syllab = "".join(items[:-1])  # syllable without tone
        tone = items[-1]
        firstvowel = re.search(r"[aeiou]", syllab)
        if firstvowel:
            # put tone mark on first vowel letter
            inspos = firstvowel.span()[1]
        else:
            # no vowel in syllable, put on nasal codas n or m, n comes first
            firstnasal = re.search(r"[nm]", syllab)
            inspos = firstnasal.span()[1]
        syllab = syllab[0:inspos] + trdict[tone] + syllab[inspos:]
        syllab = unicodedata.normalize("NFC", syllab)
        return syllab

    def word_sep(self, items):
        # replace all syllable separators with hyphens
        # and separate syllables with hyphens if no
        # syllable separator is present
        return "-".join([i for i in items if i != "-"])

    def word_tone(self, items):
        # replace all syllable separators with hyphens
        # and separate syllables with hyphens if no
        # syllable separator is present
        return "-".join([i for i in items if i != "-"])


class Sinwz(Tctransformer):
    """Convert Teochew pengim parse tree to Sinwenz system"""

    def __init__(self):
        self.system = "sinwz"

    def NASAL(self, items):
        # Nasal will end with vowel so we can keep this simple
        syllab = "".join(items[:-1])
        return syllab + "\u0303"

    def SYLLABLE_SEP(self, value):
        # TODO: Check what syllable separators are used in Sinwenz
        # Change all syllable separators to hyphens
        return "-"

    def initial(self, items):
        trdict = {
            "INIT_BH": "bh",
            "INIT_P": "p",
            "INIT_B": "b",
            "INIT_M": "m",
            "INIT_NG": "ng",
            "INIT_N": "n",
            "INIT_GH": "gh",
            "INIT_K": "k",
            "INIT_G": "g",
            "INIT_D": "d",
            "INIT_T": "t",
            "INIT_Z": "z",
            "INIT_C": "c",
            "INIT_S": "s",
            "INIT_H": "x",
            "INIT_R": "dz",
            "INIT_L": "l",
        }
        # initials that have merged in modern Teochew
        trdict["INIT_CH"] = "z"
        trdict["INIT_CHH"] = "c"
        trdict["INIT_J"] = "dz"
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            "MED_AI": "ai",
            "MED_AU": "ao",
            "MED_IA": "ia",
            "MED_IAU": "iao",
            "MED_IEU": "iao", # TODO merger?
            "MED_IOU": "iao",
            "MED_IU": "iu",
            "MED_IE": "io",
            "MED_IO": "io",
            "MED_OI": "oi",
            "MED_OU": "ou",
            "MED_UAI": "uai",
            "MED_UA": "ua",
            "MED_UE": "ue",
            "MED_UI": "ui",
            "MED_A": "a",
            "MED_V": "y",
            "MED_E": "e",
            "MED_I": "i",
            "MED_O": "o",
            "MED_U": "u",
        }
        return trdict[items[0].type]

    def codastops(self, items):
        trdict = {
            "COD_P": "p",
            "COD_K": "q",
            "COD_H": "q",
        }
        return trdict[items[0].type]

    def codanasal(self, items):
        trdict = {
            "COD_M": "m",
            "COD_NG": "ng",
            "COD_N": "n",
        }
        return trdict[items[0].type]

    def tone(self, items):
        # Only return the citation tone
        return str(items[0])

    def syllable_tone(self, items):
        # Check if syllable begins with i or u
        pre = list("".join([str(i) for i in items]))
        if pre[0] == "i" and len(pre) > 1:
            pre[0] = "j"
        elif pre[0] == "u" and len(pre) > 1:
            pre[0] = "w"
        return "".join(pre)

    def syllable_toneless(self, items):
        # Check if syllable begins with i or u
        pre = list("".join([str(i) for i in items]))
        if pre[0] == "i" and len(pre) > 1:
            pre[0] = "j"
        elif pre[0] == "u" and len(pre) > 1:
            pre[0] = "w"
        return "".join(pre)

    def word_sep(self, items):
        # replace all syllable separators with hyphens
        # and separate syllables with hyphens if no
        # syllable separator is present
        return "-".join([i for i in items if i != "-"])

    def word_tone(self, items):
        # replace all syllable separators with hyphens
        # and separate syllables with hyphens if no
        # syllable separator is present
        return "-".join([i for i in items if i != "-"])


class Zapngou(Tctransformer):
    # This is a special case because the finals are terminals and not
    # decomposed further to medials+coda
    INITS = ["柳", "邊", "求", "去", "地", "頗", "他", "貞", "入", "時", "文", "語", "出", "喜"]

    def NASAL(self, value):
        return "n"

    def initial(self, items):
        trdict = {
            "INIT_L": "柳",
            "INIT_N": "柳(n)",  # merged in Minnan/Hokkien
            "INIT_B": "邊",
            "INIT_M": "邊(m)",  # merged in Minnan/Hokkien
            "INIT_G": "求",
            "INIT_NG": "求(ng)",  # merged in Minnan/Hokkien
            "INIT_K": "去",
            "INIT_D": "地",
            "INIT_P": "頗",
            "INIT_T": "他",
            "INIT_Z": "貞",
            "INIT_R": "入",
            "INIT_S": "時",
            # null 英
            "INIT_BH": "文",
            "INIT_GH": "語",
            "INIT_C": "出",
            "INIT_H": "喜",
        }
        # initials that have merged in modern Teochew
        trdict["INIT_CH"] = "貞"
        trdict["INIT_CHH"] = "出"
        trdict["INIT_J"] = "入"

        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            term: TERMINALS["medials"][term]["dieghv"]
            for term in TERMINALS["medials"]
            if "dieghv" in TERMINALS["medials"][term]
        }
        return trdict[items[0].type]

    def codastops(self, items):
        trdict = {
            term: TERMINALS["codastops"][term]["dieghv"]
            for term in TERMINALS["codastops"]
            if "dieghv" in TERMINALS["codastops"][term]
        }
        trdict["COD_T"] = "g"  # Dieghv does not have stop -t
        return trdict[items[0].type]

    def codanasal(self, items):
        trdict = {
            term: TERMINALS["codanasals"][term]["dieghv"]
            for term in TERMINALS["codanasals"]
            if "dieghv" in TERMINALS["codanasals"][term]
        }
        trdict["COD_N"] = "ng"  # Dieghv does not have coda n
        return trdict[items[0].type]

    def final(self, items):
        trdict = {
            "ung": "君",
            "uk": "君",
            "ieng": "堅",  # additional to Xu
            "iang": "堅",
            "iek": "堅",  # additional to Xu
            "iak": "堅",
            "im": "金",
            "ip": "金",
            "ui": "歸",
            "uih": "歸",
            "ia": "佳",
            "iah": "佳",
            "ang": "干",
            "ak": "干",
            "ong": "公",
            "ok": "公",
            "uai": "乖",
            "uain": "乖（鼻）",  # not in Xu, only in suain 'mango'
            "uaih": "乖",
            "eng": "經",
            "ek": "經",
            "ueng": "關",  # different from Xu
            "uek": "關",  # different from Xu
            "ou": "孤",
            "ouh": "孤",
            "iau": "驕",
            "iou": "驕",
            "ieu": "驕",
            "iauh": "驕",
            "iouh": "驕",
            "ieuh": "驕",
            "oi": "雞",
            "oih": "雞",
            "iong": "恭",
            "iok": "恭",
            "o": "高",
            "oh": "高",
            "ai": "皆",
            "aih": "皆",
            "ing": "斤",  # different from Xu
            "ik": "斤",  # different from Xu
            "ion": "薑",
            "ionh": "薑",
            "ien": "薑",
            "ienh": "薑",
            "am": "甘",
            "ap": "甘",
            "ua": "柯",
            "uah": "柯",
            "ang": "江",
            "ak": "江",
            "iam": "兼",
            "iap": "兼",
            "iem": "兼",
            "iep": "兼",
            "au": "交",
            "auh": "交",
            "e": "家",
            "eh": "家",
            "ue": "瓜",
            "ueh": "瓜",
            "a": "膠",
            "ah": "膠",
            "u": "龜",
            "uh": "龜",
            "vng": "扛",
            "ng": "扛",
            "vk": "扛",
            "i": "枝",
            "ih": "枝",
            "iu": "鳩",
            "iuh": "鳩",
            "uan": "官",
            "uanh": "官",
            "v": "車",
            "vh": "車",
            "an": "柑",
            "anh": "柑",
            "en": "更",
            "enh": "更",
            "ia": "京",
            "ian": "京（鼻）",
            "iah": "京",
            "ianh": "京（鼻）",
            "io": "蕉",
            "ioh": "蕉",
            "ie": "蕉",
            "ieh": "蕉",
            "iang": "姜",
            "iak": "姜",
            "in": "天",
            "inh": "天",
            "uang": "光",
            "uak": "光",
            "oin": "間",
            "oinh": "間",
        }
        pre = "".join([str(i) for i in items])
        if pre in trdict:
            return trdict[pre]
        else:
            return pre

    def tone(self, items):
        trdict = {
            "1": "上平",
            "2": "上上",
            "3": "上去",
            "4": "上入",
            "5": "下平",
            "6": "下上",
            "7": "下去",
            "8": "下入",
        }
        if len(items) >= 1:
            # citation tone only
            return trdict[str(items[0])]
        else:
            return ""

    def syllable_tone(self, items):
        # If the first character is not in the list of initials, then assume
        # this is a null-initial syllable, and add 英 character. Workaround
        # because null is not permissible as a regex.
        if str(items[0])[0] not in Zapngou.INITS:
            return "【" + "英" + "".join([str(i) for i in items]) + "】"
        else:
            return "【" + "".join([str(i) for i in items]) + "】"

    def syllable_toneless(self, items):
        if str(items[0])[0] not in Zapngou.INITS:
            return "【" + "英" + "".join([str(i) for i in items]) + "】"
        else:
            return "【" + "".join([str(i) for i in items]) + "】"

    def word_sep(self, items):
        # replace all syllable separators with spaces and separate syllables
        # with spaces if no syllable separator is present
        return "".join([i for i in items if i != "-"])

    def word_tone(self, items):
        # replace all syllable separators with spaces and separate syllables
        # with spaces if no syllable separator is present
        return "".join([i for i in items if i != "-"])
