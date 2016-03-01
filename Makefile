SHELL := /bin/bash

usage:
	@echo "Usage:"
	@echo "    make release                | Release the app to PyPI."

release:
	python setup.py register -r incuna sdist upload -r incuna

test:
	coverage run test_project/manage.py test --keepdb
	coverage report
