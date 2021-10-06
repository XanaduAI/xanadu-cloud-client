PYTHON3 := $(shell which python3 2>/dev/null)

PYTHON := python3
COVERAGE := --cov=xcc --cov-report term-missing --cov-report=html:coverage_html_report
TESTRUNNER := -m pytest tests

.PHONY: help
help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  install            to install XCC"
	@echo "  wheel              to build the XCC wheel"
	@echo "  dist               to package the source distribution"
	@echo "  docs               to generate the Sphinx documentation"
	@echo "  lint               to lint the Python source files"
	@echo "  format             to format the Python source files"
	@echo "  clean              to delete all temporary, cache, and build files"
	@echo "  clean-docs         to delete all generated documentation"
	@echo "  test               to run the test suite"
	@echo "  coverage           to generate a coverage report"

.PHONY: install
install:
ifndef PYTHON3
	@echo "To install the XCC you need to have Python 3 installed"
endif
	$(PYTHON) -m pip install -e .

.PHONY: lint
lint:
	$(PYTHON) -m pylint xcc tests/*.py

.PHONY: format
format:
	$(PYTHON) -m black -l 100 xcc tests
	$(PYTHON) -m isort --profile black xcc tests

.PHONY: wheel
wheel:
	$(PYTHON) setup.py bdist_wheel

.PHONY: dist
dist:
	$(PYTHON) setup.py sdist

.PHONY : clean
clean:
	rm -rf build
	rm -rf dist
	rm -rf tests/__pycache__
	rm -rf xcc/__pycache__
	rm -rf xcc/interfaces/__pycache__

.PHONY : docs
docs:
	make -C docs html

.PHONY : clean-docs
clean-docs:
	rm -rf docs/api
	make -C docs clean

test:
	$(PYTHON) $(TESTRUNNER)

coverage:
	@echo "Generating coverage report..."
	$(PYTHON) $(TESTRUNNER) $(COVERAGE)