#!/usr/bin/env python3

import re
import json

from importlib_resources import files
from lark import Transformer

# Load terminals data
TERMINALS = json.loads(files("parsetc").joinpath("terminals.json").read_text())


class Gdpi(Transformer):
    """Convert Teochew pengim parse tree to Gengdang Pêng'im"""

    def NASAL(self, value):
        return "n"

    def initial(self, items):
        trdict = {
            term: TERMINALS["initials"][term]["gdpi"]
            for term in TERMINALS["initials"]
            if "gdpi" in TERMINALS["initials"][term]
        }
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            term: TERMINALS["medials"][term]["gdpi"]
            for term in TERMINALS["medials"]
            if "gdpi" in TERMINALS["medials"][term]
        }
        return trdict[items[0].type]

    def coda(self, items):
        return "".join([str(i) for i in items])

    def codastops(self, items):
        trdict = {
            term: TERMINALS["codastops"][term]["gdpi"]
            for term in TERMINALS["codastops"]
            if "gdpi" in TERMINALS["codastops"][term]
        }
        trdict["COD_T"] = "g"  # Gengdang Pêng'im does not have stop -t
        return trdict[items[0].type]

    def codanasal(self, items):
        trdict = {
            term: TERMINALS["codanasals"][term]["gdpi"]
            for term in TERMINALS["codanasals"]
            if "gdpi" in TERMINALS["codanasals"][term]
        }
        trdict["COD_N"] = "ng"  # Gengdang Pêng'im does not have coda n
        return trdict[items[0].type]

    def final(self, items):
        return "".join([str(i) for i in items])

    def tone(self, items):
        if len(items) == 1:
            return str(items[0])
        elif len(items) == 2:
            return str(items[0]) + "(" + str(items[1]) + ")"
        else:
            return ""

    def syllable_tone(self, items):
        return "".join([str(i) for i in items])

    def syllable_toneless(self, items):
        return "".join([str(i) for i in items])

    def word_sep(self, items):
        return "".join(items)

    def sentence(self, items):
        return "".join(items)


class Ggnn(Transformer):
    """Convert Teochew pengim parse tree to Gaginang Peng'im"""

    def NASAL(self, value):
        return "ñ"

    def initial(self, items):
        trdict = {
            term: TERMINALS["initials"][term]["ggnn"]
            for term in TERMINALS["initials"]
            if "ggnn" in TERMINALS["initials"][term]
        }
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            term: TERMINALS["medials"][term]["ggnn"]
            for term in TERMINALS["medials"]
            if "ggnn" in TERMINALS["medials"][term]
        }
        return trdict[items[0].type]

    def coda(self, items):
        return "".join([str(i) for i in items])

    def codastops(self, items):
        trdict = {
            term: TERMINALS["codastops"][term]["ggnn"]
            for term in TERMINALS["codastops"]
            if "ggnn" in TERMINALS["codastops"][term]
        }
        return trdict[items[0].type]

    def codanasal(self, items):
        trdict = {
            term: TERMINALS["codanasals"][term]["ggnn"]
            for term in TERMINALS["codanasals"]
            if "ggnn" in TERMINALS["codanasals"][term]
        }
        return trdict[items[0].type]

    def final(self, items):
        return "".join([str(i) for i in items])

    def tone(self, items):
        if len(items) == 1:
            return str(items[0])
        elif len(items) == 2:
            return str(items[0]) + "(" + str(items[1]) + ")"
        else:
            return ""

    def syllable_tone(self, items):
        return "".join([str(i) for i in items])

    def syllable_toneless(self, items):
        return "".join([str(i) for i in items])

    def word_sep(self, items):
        return "".join(items)

    def sentence(self, items):
        return "".join(items)


class Tlo(Transformer):
    """Convert Teochew pengim parse tree to Tie-lo"""

    def NASAL(self, value):
        return "nn"

    def SYLLABLE_SEP(self, value):
        # Change all syllable separators to hyphens
        return "-"

    def initial(self, items):
        trdict = {
            term: TERMINALS["initials"][term]["tlo"]
            for term in TERMINALS["initials"]
            if "tlo" in TERMINALS["initials"][term]
        }
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            term: TERMINALS["medials"][term]["tlo"]
            for term in TERMINALS["medials"]
            if "tlo" in TERMINALS["medials"][term]
        }
        return trdict[items[0].type]

    def coda(self, items):
        return "".join([str(i) for i in items])

    def codastops(self, items):
        trdict = {
            term: TERMINALS["codastops"][term]["tlo"]
            for term in TERMINALS["codastops"]
            if "tlo" in TERMINALS["codastops"][term]
        }
        return trdict[items[0].type]

    def codanasal(self, items):
        trdict = {
            term: TERMINALS["codanasals"][term]["tlo"]
            for term in TERMINALS["codanasals"]
            if "tlo" in TERMINALS["codanasals"][term]
        }
        return trdict[items[0].type]

    def final(self, items):
        return "".join([str(i) for i in items])

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
        # TODO put tone mark on first vowel letter else on first letter of final
        syllab = "".join(items[:-1])  # syllable without tone
        tone = items[-1]
        firstvowel = re.search(r"[aeiou]", syllab)
        if firstvowel:
            # put tone mark on first vowel letter
            inspos = firstvowel.span()[1]
            syllab = syllab[0:inspos] + trdict[tone] + syllab[inspos:]
        else:
            # no vowel in syllable, put on first character
            syllab = syllab[0] + trdict[tone] + syllab[1:]
        return syllab

    def syllable_toneless(self, items):
        return "".join([str(i) for i in items])

    def word_sep(self, items):
        # replace all syllable separators with hyphens
        # and separate syllables with hyphens if no
        # syllable separator is present
        return "-".join([i for i in items if i != "-"])

    def sentence(self, items):
        return "".join(items)


class Duffus(Transformer):
    """Convert Teochew pengim parse tree to Duffus system"""

    def NASAL(self, value):
        return "\u207f"

    def SYLLABLE_SEP(self, value):
        # Change all syllable separators to hyphens
        return "-"

    def initial(self, items):
        trdict = {
            "INIT_BH": "b",
            "INIT_P": "ph",
            "INIT_B": "p",
            "INIT_M": "m",
            "INIT_NG": "ng",
            "INIT_N": "n",
            "INIT_GH": "g",
            "INIT_K": "kh",
            "INIT_G": "k",
            "INIT_D": "t",
            "INIT_T": "th",
            "INIT_Z": "ts",
            "INIT_C": "tsh",
            "INIT_S": "s",
            "INIT_H": "h",
            "INIT_R": "z",
            "INIT_L": "l",
        }
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            "MED_AI": "ai",
            "MED_AU": "au",
            "MED_IA": "ia",
            "MED_IAU": "iau",
            "MED_IEU": "ieu",
            "MED_IOU": "iou",
            "MED_IU": "iu",
            "MED_IE": "ie",
            "MED_IO": "io",
            "MED_OI": "oi",
            "MED_OU": "ou",
            "MED_UAI": "uai",
            "MED_UA": "ua",
            "MED_UE": "ue",
            "MED_UI": "ui",
            "MED_A": "a",
            "MED_V": "ṳ",
            "MED_E": "e",
            "MED_I": "i",
            "MED_O": "o",
            "MED_U": "u",
        }
        return trdict[items[0].type]

    def coda(self, items):
        return "".join([str(i) for i in items])

    def codastops(self, items):
        trdict = {
            "COD_P": "p",
            "COD_K": "k",
            "COD_H": "h",
            "COD_T": "t",
        }
        return trdict[items[0].type]

    def codanasal(self, items):
        trdict = {
            "COD_M": "m",
            "COD_NG": "ng",
            "COD_N": "n",
        }
        return trdict[items[0].type]

    def final(self, items):
        return "".join([str(i) for i in items])

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
            "6": "\u0303",
            "7": "\u0304",
            "8": "\u0307",
            "0": "",
        }
        # TODO put tone mark on first vowel letter else on first letter of final
        syllab = "".join(items[:-1])  # syllable without tone
        tone = items[-1]
        firstvowel = re.search(r"[aeiou]", syllab)
        if firstvowel:
            # put tone mark on first vowel letter
            inspos = firstvowel.span()[1]
            syllab = syllab[0:inspos] + trdict[tone] + syllab[inspos:]
        else:
            # no vowel in syllable, put on first character
            syllab = syllab[0] + trdict[tone] + syllab[1:]
        return syllab

    def syllable_toneless(self, items):
        return "".join([str(i) for i in items])

    def word_sep(self, items):
        # replace all syllable separators with hyphens
        # and separate syllables with hyphens if no
        # syllable separator is present
        return "-".join([i for i in items if i != "-"])

    def sentence(self, items):
        return "".join(items)


class Sinwz(Transformer):
    """Convert Teochew pengim parse tree to Sinwenz system"""

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
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            "MED_AI": "ai",
            "MED_AU": "ao",
            "MED_IA": "ia",
            "MED_IAU": "iao",
            "MED_IEU": "iao",
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

    def coda(self, items):
        return "".join([str(i) for i in items])

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

    def final(self, items):
        return "".join([str(i) for i in items])

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

    def sentence(self, items):
        return "".join(items)


class Zapngou(Transformer):
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
        return trdict[items[0].type]

    def medial(self, items):
        trdict = {
            term: TERMINALS["medials"][term]["dieghv"]
            for term in TERMINALS["medials"]
            if "dieghv" in TERMINALS["medials"][term]
        }
        return trdict[items[0].type]

    def coda(self, items):
        return "".join([str(i) for i in items])

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

    def sentence(self, items):
        return "".join(items)
