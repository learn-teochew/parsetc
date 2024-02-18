import re
import unicodedata

INPUT_SYS = ["dieghv", "gdpi", "ggn", "ggnn", "tlo", "duffus"]


def diacritics_syllable_parse(syllable, system):
    """Parse a syllable with tone diacritics to tone number

    Tie-lo or Duffus systems only. Also decomposes compound characters, needed
    for ṳ which can be either single character or combining.

    Will not complain if a syllable has two diacritics. Beware!

    Returns
    -------
    (str, int) : base syllable string, tone number. Tone 0 not supported
    """
    tonemarks = {
        "tlo": {
            769: 2,  # hex 0x301
            768: 3,  # 0x300
            770: 5,  # 0x302
            774: 6,  # 0x306
            780: 6,  # 0x30C combining caron, often confused with combining breve
            772: 7,  # 0x304
        },
        "duffus": {
            769: 2,  # hex 0x301
            768: 3,  # 0x300
            770: 5,  # 0x302
            771: 6,  # 0x303
            772: 7,  # 0x304
            781: 8,  # 0x30D # vertical line above
            775: 8,  # 0x307 # dot above - variant
        },
    }
    notone = []
    tone = 1  # default tone

    decomp = [ord(i) for i in unicodedata.normalize("NFD", syllable)]
    # Check for tone diacritic, should be only one
    tones = [tonemarks[system][i] for i in decomp if i in tonemarks[system]]
    if len(tones) == 1:
        tone = tones[0]
    elif len(tones) > 1:
        pass  # TODO complain
    # All other characters
    notone = [chr(i) for i in decomp if i not in tonemarks[system]]

    return ("".join(notone), tone)


def preprocess(text, system):
    """Preprocess input text (lowercase, tone diacritics to numbers)

    Tone diacritics used by Tie-lo and Duffus systems only. Conversion of tone
    diacritics to numeric assumes that all syllables have tones marked!
    Conversion is impossible otherwise, because tone1 cannot be distinguished
    from unmarked tone

    Parameters
    ----------
    text : str
        Input text, without linebreaks
    system : str
        Input scheme

    Returns
    -------
    str
        Input with tone numbers instead of diacritics
    """
    text = text.lower()
    if system in ["tlo", "duffus"]:
        out = []
        for elem in re.split(r"([\s,\.\'\"\?\!\-\;\:]+)", text):  # TODO hacky
            if elem != "" and not re.search(r"([\d\s,\.\'\"\?\!\-\;\:]+)", elem):
                out.append(
                    "".join([str(i) for i in diacritics_syllable_parse(elem, system)])
                )
            else:
                out.append(elem)
        return "".join(out)
    else:
        return text
