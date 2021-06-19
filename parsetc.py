#!/usr/bin/env python3

import re
import unicodedata
import argparse
import translit
import sys
import json
from textwrap import dedent
from lark import Lark

# Available input formats for parsers
# load terminals data
with open("terminals.json") as fh:
    TERMINALS = json.load(fh)

# grammar rules per transcription system
# written in Lark format
# 'common' are rules that are common to all systems
RULES = {}

RULES['common'] = """
// Three options for dealing with potentially ambiguous syllable parsing
// 1. all syllables in a word must be separated either by tone number or punctuation
sentence : word_sep ( ( PUNCTUATION | SPACE )+ word_sep )* [ PUNCTUATION | SPACE ]
word_sep : ( syllable_toneless [ SYLLABLE_SEP word_sep ] ) | ( syllable_tone [ word_sep ] )
// 2. syllable separation not explicit, tone numbers and syllable separators are optional
// leave it to the parser, which may make surprising choices
sentence_ambig : word ( [ PUNCTUATION | SPACE ] word )* [ PUNCTUATION | SPACE ]
word : ( syllable SYLLABLE_SEP? )+
// 3. all syllables must have tone number (including 0), so no ambiguities about syllable separation
sentence_tone : word_tone ( ( PUNCTUATION  | SPACE )+ word_tone )* [ PUNCTUATION | SPACE ]
word_tone : syllable_tone+
// Syllables
syllable : initial? final tone?
syllable_tone : initial? final tone
syllable_toneless : initial? final
// Initials
initial : INIT_BH | INIT_P  | INIT_B
        | INIT_M  | INIT_NG | INIT_N
        | INIT_GH | INIT_K  | INIT_G
        | INIT_D  | INIT_T 
        | INIT_Z  | INIT_C 
        | INIT_S  | INIT_H 
        | INIT_R  | INIT_L 
// Finals
// TODO: rule for entering tone
final :  ( medial coda ) 
      | ( medial NASAL codastops? ) 
      | medial
      | codanasal
// Medials
// longer medials are listed first to be preferentially matched
medial : MED_AI  | MED_AU  
       | MED_IA  | MED_IAU | MED_IEU | MED_IOU | MED_IU  | MED_IE  | MED_IO  
       | MED_OI  | MED_OU  
       | MED_UAI | MED_UA  | MED_UE  | MED_UI  
       | MED_A   | MED_V   | MED_E   | MED_I   | MED_O   | MED_U   
// Punctuation and spacing
PUNCTUATION : "." | "," | "?" | "!" | "'" | "-"
SPACE : " "

"""

RULES['dieghv'] = """
// Codas
coda : codanasal | codastops
codanasal : COD_M | COD_NG
codastops : COD_P | COD_K | COD_H
// Tones
tone : TONENUMBER [ "(" TONENUMBER ")" ]
TONENUMBER : "0".."8"
// syllable separators can be hyphen or apostrophes
SYLLABLE_SEP : "-" | "'" | "’"
"""

RULES['gdpi'] = """
// Codas
coda : codanasal | codastops
codanasal : COD_M | COD_NG
codastops : COD_P | COD_K | COD_H
// Tones
tone : TONENUMBER [ "(" TONENUMBER ")" ]
TONENUMBER : "0".."8"
// syllable separators can be hyphen or apostrophes
SYLLABLE_SEP : "-" | "'" | "’"
"""

RULES['ggn'] = """
// Codas
coda : codanasal | codastops
codanasal : COD_M | COD_NG
codastops : COD_P | COD_K | COD_H | COD_T
// Tones
tone : TONENUMBER [ "(" TONENUMBER ")" ]
TONENUMBER : "0".."8"
// syllable separators can be hyphen or apostrophes
SYLLABLE_SEP : "-" | "'" | "’"
"""

RULES['ggnn'] = """
// Codas
coda : codanasal | codastops
codanasal : COD_M | COD_NG | COD_N
codastops : COD_P | COD_K | COD_H | COD_T
// Tones
tone : TONENUMBER [ "(" TONENUMBER ")" ]
TONENUMBER : "0".."8"
// syllable separators can be hyphen or apostrophes
SYLLABLE_SEP : "-" | "'" | "’"
"""

PARSER_DICT = {}
for scheme in ['dieghv','gdpi','ggn','ggnn']:
    lark_rules = [
        RULES['common'],
        RULES[scheme]
    ]
    for term in TERMINALS:
        if scheme in TERMINALS[term]:
            lark_rules.append(f"{term} : \"{TERMINALS[term][scheme]}\"")
    PARSER_DICT[scheme] = Lark(
            "\n".join(lark_rules),
            start='sentence')

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
