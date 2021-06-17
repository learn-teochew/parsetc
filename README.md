Parsing tools for Teochew phonetic spelling
===========================================

Parse and convert between different Teochew phonetic spelling schemes.

Read from:

 * Geng'dang Pêng'im 廣東拼音 (`gdpi`)
 * Gaginang Peng'im 家己儂拼音 (`ggn`)
 * Gaginang Peng'im with coda `-n` allowed (nasalization written with `ñ`
   instead) (`ggnn`)
 * Dieghv 潮語 (`dieghv`)

Write to all the above, plus:

 * Tie-tsiann-hue 潮正會, also known as Tie-lo 潮羅 (`tlo`)
 * Duffus system (`duffus`)

Orthographic conventions for input text:

 * Text must be in lower case
 * Syllables may be written with or without tone numbers
 * Syllables may be combined into words for legibility
 * If syllables are combined into words, they must have tone numbers (e.g.
   `diê5ziu1`), or use a syllable separator character if tone numbers are
   omitted (e.g. `diê-ziu` or `pêng'im`). This is either a hyphen or single
   apostrophe. This is because of ambiguous parsings, e.g. `pê-ngi-m` instead
   of `pêng-im`, which in general can only be dealt with by usage frequency,
   which is not available.

Parsing makes use of the [`lark`
library](https://lark-parser.readthedocs.io/en/latest/)
