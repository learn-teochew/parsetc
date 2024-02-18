install:
	pip install --editable .

test1: test-teochew-parse test-cantonese-parse

test2: test-teochew-translate test-cantonese-translate

test-teochew-parse:
	cat examples/teochew.dieghv.sep.txt | parsetc -l Teochew -i dieghv -p
	cat examples/teochew.dieghv.tones.txt | parsetc -l Teochew -i dieghv -p

test-teochew-translate:
	cat examples/teochew.dieghv.sep.txt | parsetc -l Teochew -i dieghv --all
	cat examples/teochew.duffus.txt | parsetc -l Teochew -i duffus --all

test-cantonese-parse:
	cat examples/cantonese.cpy.txt | parsetc -l Cantonese -i cpy -p
	cat examples/cantonese.jp.txt | parsetc -l Cantonese -i jp -p

test-cantonese-translate:
	cat examples/cantonese.cpy.txt | parsetc -l Cantonese -i cpy --all
	cat examples/cantonese.jp.txt | parsetc -l Cantonese -i jp --all

test3:
	echo 'tsioh thâu' | parsetc -i duffus -a

black:
	black src/parsetc/parsetc.py
	black src/parsetc/Teochew/*.py
	black src/parsetc/Cantonese/*.py

build:
	python -m build

upload:
	twine upload --skip-existing dist/*

help:
	echo "install test1 test2 build upload"
