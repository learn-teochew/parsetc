import re
import unicodedata

INPUT_SYS = ["jp"]

def diacritics_syllable_parse(syllable, system):
    """Parse a syllable with tone diacritics to tone number

    Yale system only. Also decomposes compound characters.

    Will not complain if a syllable has two diacritics. Beware!

    Returns
    -------
    (str, str) : base syllable string, tone number. Tone 0 not supported
    """
    tonemarks = {
        "yale": {
            772: "1a",  # combining macron
            768: "1b",  # combining grave
            769: "2" ,  # combining acute
        },
    }
    notone = []
    tone = 3  # unmarked

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

    Arguments
    ---------
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
    if system in ["yale"]:
        out = []
        for elem in re.split(r"([\s,\.\'\"\?\!\-]+)", text):  # TODO hacky
            if elem != "" and not re.match(r"([\s,\.\'\"\?\!\-]+)", elem):
                out.append(
                    "".join([str(i) for i in diacritics_syllable_parse(elem, system)])
                )
            else:
                out.append(elem)
        return "".join(out)
    else:
        return text



