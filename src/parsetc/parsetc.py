#!/usr/bin/env python3

import re
import unicodedata
import argparse
import sys
import json
import importlib

from parsetc import __version__

from importlib_resources import files
from lark import Lark
from lark import __version__ as lark_version


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


def print_version():
    """Report package and dependency versions"""
    print("parsetc " + __version__)
    print("lark " + lark_version)
    print("unicodedata unidata_version " + unicodedata.unidata_version)
    return


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
                    "9": "⁹",
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


def get_args():
    parser = argparse.ArgumentParser(
        description="""
        Parse and convert romanized Chinese between different phonetic spelling schemes.
        Text is read from STDIN, output written to STDOUT.
        """
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default="Teochew",
        choices=["Teochew"],
        help="Language/dialect module to use"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="gdpi",
        help="Input romanization",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="tlo",
        help="Output romanization",
    )
    parser.add_argument(
        "--show_options",
        action="store_true",
        help="Show available languages and transcription schemes"
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
        help="Tone numbers in superscript",
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
        help="Show parse rules in Lark format for input scheme specified with --input (other options ignored)",
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
    return args


def main():
    args = get_args()

    if args.version:
        print_version()
        exit()

    # Dynamically load data based on input language
    # Load transformers and preprocessing functions
    mytranslit = importlib.import_module(f"parsetc.{args.language}.translit")
    myparser = importlib.import_module(f"parsetc.{args.language}.parser")
    # Load parser data
    LARK_DICT, PARSER_DICT = load_parser_data(
        shared_fn=f"{args.language}/shared.lark",
        terminals_fn=f"{args.language}/terminals.json",
        extends_fn=f"{args.language}/extends.json",
        systems=myparser.INPUT_SYS,
    )

    if args.show_lark:
        try:
            print(LARK_DICT[args.input])
        except KeyError:
            print(
                f"Invalid input scheme {args.input}, must be one of {', '.join(list(LARK_DICT.keys()))}",
                file=sys.stderr,
            )
        exit()

    if args.show_options:
        print(f"Available schemes for language {args.language}")
        print(f"  input  : {' '.join(myparser.INPUT_SYS) }")
        print(f"  output : {' '.join(mytranslit.TRANSFORMER_DICT.keys()) }")
        exit()

    for intext in sys.stdin:
        outtext = ""
        intext = intext.rstrip()
        if args.delim_only:
            in_splits = intext.split(args.delim_only)
            for i in range(len(in_splits)):
                if i % 2 == 1:
                    outtext += transliterate(
                        myparser.preprocess(in_splits[i], args.input),
                        i=args.input,
                        o=args.output,
                        parser_dict=PARSER_DICT,
                        transformer_dict=mytranslit.TRANSFORMER_DICT,
                        superscript_tone=args.superscript_tone,
                    )
                else:
                    outtext += in_splits[i]
        else:
            intext = myparser.preprocess(intext, args.input)
            if args.parse_only:
                parsetree = PARSER_DICT[args.input].parse(intext)
                print(parsetree.pretty())
            elif args.all:
                out = transliterate_all(
                    intext,
                    i=args.input,
                    parser_dict=PARSER_DICT,
                    transformer_dict=mytranslit.TRANSFORMER_DICT,
                )
                print("\t".join(["INPUT", intext]))
                for line in out:
                    print("\t".join(list(line)))
            else:
                outtext = transliterate(
                    intext,
                    i=args.input,
                    o=args.output,
                    parser_dict=PARSER_DICT,
                    transformer_dict=mytranslit.TRANSFORMER_DICT,
                    superscript_tone=args.superscript_tone,
                )
        print(outtext)
