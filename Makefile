.DEFAULT_GOAL := help
define PRINT_HELP_PYSCRIPT
import re, sys

target_help_map = {}
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		target_help_map[target] = help
for target in sorted(target_help_map):
	print("%-20s %s" % (target, target_help_map[target]))
endef
export PRINT_HELP_PYSCRIPT

VENV_UPDATE_VERSION ?= 2.1.1

REQUIREMENTS ?= requirements-minimal.txt
REQUIREMENTS_DEV ?= requirements-dev-minimal.txt
REQUIREMENTS_BOOTSTRAP ?= requirements-bootstrap.txt

VIRTUALENV_PYTHON_VERSION ?= 2.7
VIRTUALENV_PATH ?= virtualenv_run
VENV_BINARY ?= bin/venv-update


.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean
clean: clean-build clean-pyc clean-test clean-virtualenv clean-venv-update clean-docs ## remove all build, test, coverage and Python artifacts


.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: clean-virtualenv
clean-virtualenv: ## remove virtual environment
	rm -fr $(VIRTUALENV_PATH)

.PHONY: clean-venv-update
clean-venv-update: ## remove venv-update binary
	rm -fr $(VENV_BINARY)

.PHONY: clean-docs
clean-docs:  ## remove documentation artifacts
	rm -f docs/swagger_code_generator*.rst
	rm -f docs/tests*.rst
	rm -f docs/modules.rst

$(VENV_BINARY): ## download venv-update
	wget https://raw.githubusercontent.com/Yelp/venv-update/v$(VENV_UPDATE_VERSION)/venv_update.py -O $(VENV_BINARY)
	chmod a+x $(VENV_BINARY)

$(VIRTUALENV_PATH): $(VENV_BINARY) $(REQUIREMENTS) $(REQUIREMENTS_DEV) $(REQUIREMENTS_BOOTSTRAP)  ## create a new python virtual environment
	$(VENV_BINARY) \
		venv= $(VIRTUALENV_PATH) --python=python$(PYTHON_VERSION) \
		install= -r $(REQUIREMENTS) -r $(REQUIREMENTS_DEV) \
		bootstrap-deps= -r $(REQUIREMENTS_BOOTSTRAP) \
		pip-command= pymonkey pip-custom-platform -- pip-faster install --upgrade --prune

.PHONY: install-hooks
install-hooks: $(VIRTUALENV_PATH)  ## install pre-commit hooks on this repository
	$(VIRTUALENV_PATH)/bin/pre-commit install -f --install-hooks

.PHONY: development
development: $(VIRTUALENV_PATH) install-hooks ## prepare development environment
	@true

.PHONY: tests
tests: test  ## run tests on every Python 3.5
	@true

.PHONY: test
test: ## run tests on every Python 3.5
	tox -e py35

.PHONY: test-all
test-all: ## run tests on every Python version
	tox

.PHONY: coverage
coverage: ## check code coverage quickly with the default Python
	tox -e coverage
	coverage html
	open htmlcov/index.html

.PHONY: docs
docs: clean-docs ## generate Sphinx HTML documentation, including API docs
	tox -e docs
	open docs/_build/html/index.html
