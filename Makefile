VIRTUAL_ENV ?= .venv

all: help

.PHONY: help
help:
	@echo space-diner
	@echo TODO

.PHONY: install
install:
	if [ ! -f $(VIRTUAL_ENV)/bin/python3 ]; then python3 -m venv $(VIRTUAL_ENV); fi
	$(VIRTUAL_ENV)/bin/python3 -m pip install -r requirements.txt

.PHONY: run
run:
	$(VIRTUAL_ENV)/bin/python3 -m spacediner

.PHONY: build
build:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	$(VIRTUAL_ENV)/bin/python3 -m build
