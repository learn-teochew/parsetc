Parsing and conversion of Teochew Chinese romanizations
=======================================================

[![PyPI version shields.io](https://img.shields.io/pypi/v/parsetc.svg)](https://pypi.python.org/pypi/parsetc/)
![GitHub License](https://img.shields.io/github/license/learn-teochew/parsetc)

Parse and convert between different Teochew romanized spelling schemes.


Available romanization schemes for Teochew
------------------------------------------

### Input

 * Geng'dang Pêng'im 廣東拼音 (`gdpi`)
 * Gaginang Peng'im 家己儂拼音 (`ggn`)
 * Gaginang Peng'im with coda `-n` allowed (nasalization written with `ñ`
   instead) (`ggnn`)
 * Dieghv 潮語 (`dieghv`);
   [(source)](https://kahaani.github.io/gatian/appendix1/index.html)
 * Tie-tsiann-hue 潮正會, also known as Tie-lo 潮羅 (`tlo`);
   [(source)](http://library.hiteo.pw/book/wagpzbkv.html)
 * Duffus system (`duffus`), also known as Pe̍h-ūe-jī (PUJ);
   [(source)](https://archive.org/details/englishchinesev00duffgoog)


### Output

`gdpi`, `ggnn`, `tlo`, `duffus`, `dieghv`, plus:

 * Teochew Sinwenz (`sinwz`);
   [(source)](http://eresources.nlb.gov.sg/newspapers/Digitised/Page/nysp19391115-1.1.22)
 * Traditional initial-final categories (`15`) from 《彙集雅俗通十五音》 also
   known as 《擊木知音》, based on the analysis by 徐宇航
   「《擊木知音》音系之再研究」 (2014)


Other languages
---------------

This tool was originally developed for Teochew, but can be extended in the
future to other dialects or languages. An experimental Cantonese module
(`--language Cantonese`) with Jyutping (`jp`) and Cantonese Pinyin (`cpy`) is
available.


Orthographic requirements for input text
----------------------------------------

 * Text must be in lower case
 * Syllables may be written with or without tone numbers
 * Syllables may be combined into words for legibility, i.e. [word-segmented
   writing](https://en.wikipedia.org/wiki/Chinese_word-segmented_writing)
 * If syllables are combined into words, they must either have tone numbers
   (e.g. `diê5ziu1`), or use a syllable separator character (e.g. `diê-ziu` or
   `pêng'im`, or `diê5-ziu1`). The separator character is either a hyphen or
   single apostrophe. This is because of ambiguous parsings, e.g. `pê-ngi-m`
   instead of `pêng-im`, which in general can only be dealt with by usage
   frequency, which is not available.
 * If syllable separator characters are used, they must be used consistently.
   Mixing conventions may cause unexpected parsing errors.


Installation
------------

`parsetc` requires Python 3 and [`lark`](https://lark-parser.readthedocs.io/en/latest/) v1.1.

Install latest release with `pip` from PyPI:

```bash
pip install parsetc
```

If you are interested in latest development version, you can clone this
repository and checkout the `dev` branch, then install with `pip` from source
code:

```bash
pip install .
```

See help message:

```bash
parsetc --help
```

View available input and output schemes for Teochew:

```bash
parsetc --language Teochew --show_options
```


Usage
-----

### Command line tool

Input text is read line-by-line from STDIN. Output is written to STDOUT.

The language (`--language` or `-l`) is `Teochew` by default.

```bash
# output in Tie-lo
echo 'ua2 ain3 oh8 diê5ghe2, ain3 dan3 diê5ziu1 uê7.' | parsetc -i gdpi -o tlo
# all available output romanizations
echo 'ua2 ain3 oh8 diê5ghe2, ain3 dan3 diê5ziu1 uê7.' | parsetc -i gdpi --all
```

Testing with provided example text:

```bash
# Example with tone numbers but no syllable separators
cat examples/dieghv.tones.txt | parsetc -i dieghv --all
# Example with hyphens as syllable separators
cat examples/dieghv.sep.txt | parsetc -i dieghv --all
```


### Python module

Updated instructions coming soon...


Related projects
----------------

### From Learn-Teochew

We use `parsetc` to convert Teochew opera transcriptions into different
romanization systems for the [Learn Teochew
Opera](https://learn-teochew.github.io/tc-opera/transcriptions) website.

How to type the special diacritics like `ṳ, o̍, o͘` in some romanization systems?
If you use MacOS X, check out our [custom keyboard
layouts](https://github.com/learn-teochew/POJ-variants-keyboard)


### Others

* [taibun](https://github.com/andreihar/taibun) - Transliterator and tokenizer
  for Taiwanese Hokkien
