install:
	pip install --editable .
test1:
	cat examples/dieghv.sep.txt | parsetc -i dieghv -p
	cat examples/dieghv.tones.txt | parsetc -i dieghv -p
test2:
	cat examples/dieghv.sep.txt | parsetc -i dieghv --all
	cat examples/duffus.txt | parsetc -i duffus --all
black:
	black src/parsetc/*.py
build:
	python -m build
upload:
	twine upload --skip-existing dist/*
help:
	echo "install test1 test2 build upload"
