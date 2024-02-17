#!/usr/bin/env python3

import re
import unicodedata
import argparse
import sys
import json

import parsetc.translit as translit
from parsetc import __version__

from importlib_resources import files
from lark import Lark
from lark import __version__ as lark_version

TEOCHEW_SYS = ["dieghv", "gdpi", "ggn", "ggnn", "tlo", "duffus"]


def load_parser_data(shared_fn, terminals_fn, extends_fn, systems):
    """Load Lark grammar for parser

    Arguments
    ---------
    shared_fn : str
        Path relative to script of lark file with shared rules
    terminals_fn : str
        Path relative to script of JSON file with terminals
    extends_fn : str
        Path relative to script of JSON file with extension rules
    systems : list
        List of short names of transcription systems

    Returns
    -------
    lark_dict
        Lark rules in text keyed by names of transcription systems
    parser_dict
        Lark parsers in dict keyed by names of transcription systems
    """
    # Load lark grammar
    # Load terminals and rule extends for each transcription system
    terminals = json.loads(files("parsetc").joinpath(terminals_fn).read_text())
    extends = json.loads(files("parsetc").joinpath(extends_fn).read_text())

    # Load rules that are shared across all systems
    with open(files("parsetc").joinpath(shared_fn)) as fh:
        shared = fh.read()

    # Available input formats for parsers
    parser_dict = {}
    lark_dict = {}
    for scheme in systems:
        lark_rules = [shared] + extends[scheme] if scheme in extends else [shared]
        for group in terminals:
            for term in terminals[group]:
                if scheme in terminals[group][term]:
                    lark_rules.append(f'{term} : "{terminals[group][term][scheme]}"')
        lark_dict[scheme] = "\n".join(lark_rules)
        parser_dict[scheme] = Lark("\n".join(lark_rules), start="start")
    return lark_dict, parser_dict


# Available output formats for transformers
TRANSFORMER_DICT = {
    "gdpi": translit.Gdpi(),
    "ggnn": translit.Ggnn(),
    "dieghv": translit.Dieghv(),
    "nosefirst": translit.Nosefirst(),
    "tlo": translit.Tlo(),
    "duffus": translit.Duffus(),
    "sinwz": translit.Sinwz(),
    "15": translit.Zapngou(),
}


def print_version():
    """Report package and dependency versions"""
    print("parsetc " + __version__)
    print("lark " + lark_version)
    print("unicodedata unidata_version " + unicodedata.unidata_version)
    return


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


# def tone_diacritic_to_numeric(text, system):
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
    if system in ["tlo", "duffus"]:
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


def transliterate_all(phrase, i, parser_dict, transformer_dict):
    """Transliterate romanized Teochew into all available output schemes

    Arguments
    ---------
    phrase : str
        Text to be transliterated, must be preprocessed to lowercase and to
        convert diacritics to tone numbers
    i : str
        Input format. Must match one of the available keys in the parser dict
    parser_dict : dict
        Lark parsers keyed by name of input format
    transformer_dict : dict
        Lark Transfomer class objects keyed by name of output formats

    Returns
    -------
    list
        Transliteration into all available schemes. Each item is a tuple of
        str: scheme name and transliteration.
    """
    try:
        t = parser_dict[i].parse(phrase)
        out = []
        for o in transformer_dict:
            out.append((o, transformer_dict[o].transform(t)))
        return out
    except KeyError:
        print(f"Unknown spelling scheme {i}")


def transliterate(phrase, i, o, parser_dict, transfomer_dict, superscript_tone=False):
    """Transliterate romanized Teochew into different spelling scheme

    Arguments
    ---------
    phrase : str
        Text to be transliterated, must be preprocessed to lowercase and to
        convert diacritics to tone numbers
    i : str
        Input format. Must match one of the available inputs
    o : str
        Output format. Must match one of the available outputs
    parser_dict : dict
        Lark parsers keyed by name of input format
    transformer_dict : dict
        Lark Transfomer class objects keyed by name of output formats
    superscript_tone : bool
        Superscript tone numbers

    Returns
    -------
    str
        Input text transliterated into requested phonetic spelling.
    """
    try:
        t = parser_dict[i].parse(phrase)
        try:
            out = transformer_dict[o].transform(t)
            if superscript_tone:
                subst = {
                    "1": "¹",
                    "2": "²",
                    "3": "³",
                    "4": "⁴",
                    "5": "⁵",
                    "6": "⁶",
                    "7": "⁷",
                    "8": "⁸",
                    "0": "⁰",
                }
                for num in subst:
                    out = out.replace(num, subst[num])
                return out
            else:
                return out
        except KeyError:
            print(f"Invalid output scheme {o}")
            print(f"Must be one of {', '.join(list(transformer_dict.keys()))}")
    except KeyError:
        print(f"Invalid input scheme {i}")
        print(f"Must be one of {', '.join(list(parser_dict.keys()))}")


def main():
    parser = argparse.ArgumentParser(
        description="""
        Parse and convert romanized Teochew between different phonetic spelling schemes

        Text is read from STDIN
        """
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="gdpi",
        help=f"Input romanization, available: {', '.join(TEOCHEW_SYS)}",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="tlo",
        help=f"Output romanization, available: {', '.join(list(TRANSFORMER_DICT.keys()))}",
    )
    parser.add_argument(
        "--parse_only",
        "-p",
        action="store_true",
        help="Only report parse in prettified format from lark (option --output ignored)",
    )
    parser.add_argument(
        "--superscript_tone",
        "-s",
        action="store_true",
        help="Tone numbers in superscript (for gdpi and ggnn output only)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Output in all available formats, tab-separated (option --output ignored)",
    )
    parser.add_argument(
        "--show_lark",
        action="store_true",
        help="Show parse rules in Lark format for input romanization (output --output ignored)",
    )
    parser.add_argument(
        "--delim_only",
        "-d",
        type=str,
        default=None,
        help="Only parse and convert text that is contained within delimiters (not compatible with --parse_only)",
    )
    parser.add_argument(
        "--version", "-v", action="store_true", help="Report version number"
    )
    args = parser.parse_args()

    if args.version:
        print_version()
        exit()

    lark_dict, parser_dict = load_parser_data(
        shared_fn="shared.lark",
        terminals_fn="terminals.json",
        extends_fn="extends.json",
        systems=TEOCHEW_SYS,
    )

    if args.show_lark:
        try:
            print(lark_dict[args.input])
        except KeyError:
            print(
                f"Invalid input scheme {args.input}, must be one of {', '.join(list(lark_dict.keys()))}",
                file=sys.stderr,
            )
        exit()

    for intext in sys.stdin:
        outtext = ""
        intext = intext.rstrip()
        if args.delim_only:
            in_splits = intext.split(args.delim_only)
            for i in range(len(in_splits)):
                if i % 2 == 1:
                    outtext += transliterate(
                        preprocess(in_splits[i], args.input),
                        i=args.input,
                        o=args.output,
                        parser_dict=parser_dict,
                        transformer_dict=TRANSFORMER_DICT,
                        superscript_tone=args.superscript_tone,
                    )
                else:
                    outtext += in_splits[i]
        else:
            intext = preprocess(intext, args.input)
            if args.parse_only:
                parsetree = parser_dict[args.input].parse(intext)
                print(parsetree.pretty())
            elif args.all:
                out = transliterate_all(
                    intext,
                    i=args.input,
                    parser_dict=parser_dict,
                    transformer_dict=TRANSFORMER_DICT,
                )
                print("\t".join(["INPUT", intext]))
                for line in out:
                    print("\t".join(list(line)))
            else:
                outtext = transliterate(
                    intext,
                    i=args.input,
                    o=args.output,
                    parser_dict=parser_dict,
                    transformer_dict=TRANSFORMER_DICT,
                    superscript_tone=args.superscript_tone,
                )
        print(outtext)
