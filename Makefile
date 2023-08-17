.PHONY: clean-pyc clean-build clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

install:
	python -m venv .venv
	./.venv/bin/python -m pip install -r requirements-dev.txt

test:
	python setup.py pytest

test-all:
	tox

coverage:
	pip install coverage
	coverage run setup.py pytest
	coverage report
	coverage xml

release: dist
	pip install twine
	python -m twine upload --non-interactive --username __token__ --password ${PYPI_TOKEN} dist/*

dist: clean
	python setup.py bdist_wheel --universal
