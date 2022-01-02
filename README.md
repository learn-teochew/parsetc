Parsing tools for Teochew phonetic spelling
===========================================

Parse and convert between different Teochew phonetic spelling schemes.


Input formats
-------------

 * Geng'dang Pêng'im 廣東拼音 (`gdpi`)
 * Gaginang Peng'im 家己儂拼音 (`ggn`)
 * Gaginang Peng'im with coda `-n` allowed (nasalization written with `ñ`
   instead) (`ggnn`)
 * Dieghv 潮語 (`dieghv`);
   [(source)](https://kahaani.github.io/gatian/appendix1/index.html)


Output formats
--------------

`gdpi`, `ggnn`, plus:

 * Tie-tsiann-hue 潮正會, also known as Tie-lo 潮羅 (`tlo`);
   [(source)](http://library.hiteo.pw/book/wagpzbkv.html)
 * Duffus system (`duffus`);
   [(source)](https://archive.org/details/englishchinesev00duffgoog)
 * Teochew Sinwenz (`sinwz`);
   [(source)](http://eresources.nlb.gov.sg/newspapers/Digitised/Page/nysp19391115-1.1.22)


Orthographic conventions for input text
---------------------------------------

 * Text must be in lower case
 * Syllables may be written with or without tone numbers
 * Syllables may be combined into words for legibility
 * If syllables are combined into words, they must have tone numbers (e.g.
   `diê5ziu1`), or use a syllable separator character if tone numbers are
   omitted (e.g. `diê-ziu` or `pêng'im`). This is either a hyphen or single
   apostrophe. This is because of ambiguous parsings, e.g. `pê-ngi-m` instead
   of `pêng-im`, which in general can only be dealt with by usage frequency,
   which is not available.


Running the script
------------------

Python 3 is required.

Install the [`lark` library](https://lark-parser.readthedocs.io/en/latest/) with pip:

```
pip install lark
```

See help message:

```
python parsetc.py --help
```

Input text is read from STDIN, no line breaks.

```
# output in Tie-lo
echo 'ua2 ain3 oh8 diê5ghe2, ain3 dan3 diê5ziu1 uê7.' | python parsetc.py -i gdpi -o tlo
# all available output romanizations
echo 'ua2 ain3 oh8 diê5ghe2, ain3 dan3 diê5ziu1 uê7.' | python parsetc.py -i gdpi --all
```
