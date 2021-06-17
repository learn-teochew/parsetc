#!/usr/bin/env python3

import re
import unicodedata
import argparse
import translit
import sys
from textwrap import dedent
from lark import Lark

# Available input formats for parsers
PARSER_DICT = {}
with open('common.lark') as fh:
    common = fh.read()
for i in ['dieghv','gdpi','ggn','ggnn']:
    with open(f'{i}.lark') as fh:
        j = fh.read()
        PARSER_DICT[i] = Lark(common + j, start='sentence')

# Available output formats for transformers
TRANSFORMER_DICT = {
    'gdpi' : translit.Gdpi(),
    'ggnn' : translit.Ggnn(),
    'tlo' : translit.Tlo(),
    'duffus' : translit.Duffus()
}


def transliterate_all(phrase, i="gdpi"):
    """Transliterate romanized Teochew into all available output schemes

    Arguments
    ---------
    phrase : str
        Text to be transliterated
    i : str
        Input format. Must match one of the available inputs

    Returns
    -------
    list
        Transliteration into all available schemes. Each item is a tuple of
        str: scheme name and transliteration.
    """
    try:
        t = PARSER_DICT[i].parse(phrase)
        out = []
        for o in TRANSFORMER_DICT:
            out.append((o, TRANSFORMER_DICT[o].transform(t)))
        return(out)
    except KeyError:
        print(f"Unknown spelling scheme {i}")


def transliterate(phrase, i='gdpi', o='tlo'):
    """Transliterate romanized Teochew into different spelling scheme

    Arguments
    ---------
    phrase : str
        Text to be transliterated
    i : str
        Input format. Must match one of the available inputs
    o : str
        Output format. Must match one of the available outputs

    Returns
    -------
    str
        Input text transliterated into requested phonetic spelling.
    """
    try:
        t = PARSER_DICT[i].parse(phrase)
        try:
            return(TRANSFORMER_DICT[o].transform(t))
        except KeyError:
            print(f'Invalid output scheme {o}')
    except KeyError:
        print(f'Invalid input scheme {i}')
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Parse and convert romanized Teochew between different phonetic spelling schemes

        Text is read from STDIN
        """)
    parser.add_argument(
        '--input', '-i', type=str, default='gdpi',
        help="Input romanization, available: gdpi, ggn, ggnn, dieghv")
    parser.add_argument(
        '--output', '-o', type=str, default='tlo',
        help="Output romanization, available: gdpi, ggnn, tlo, duffus")
    parser.add_argument(
        '--parse_only', '-p', action='store_true',
        help="Only report parse in prettified format from lark (option --output ignored)")
    parser.add_argument(
        '--all', '-a', action='store_true',
        help="Output in all available formats, tab-separated (option --output ignored)")
    args = parser.parse_args()

    intext = sys.stdin.read().rstrip()

    if args.parse_only:
        parsetree = PARSER_DICT[args.input].parse(intext)
        print(parsetree.pretty())
    elif args.all:
        out = transliterate_all(intext, i=args.input)
        print("\t".join(['INPUT', intext]))
        for line in out:
            print("\t".join(list(line)))
    else:
        print(transliterate(intext, i=args.input, o=args.output))
