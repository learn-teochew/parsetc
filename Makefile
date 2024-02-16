install:
	pip install .
test:
	cat examples/dieghv.sep.txt | parsetc -i dieghv --all
	cat examples/duffus.txt | parsetc -i duffus --all
build:
	python -m build
upload:
	twine upload --skip-existing dist/*
help:
	echo "install test build upload"
