SHELL := /bin/bash

release:
	python setup.py register -r incuna sdist upload -r incuna

