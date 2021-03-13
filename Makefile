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
	$(VIRTUAL_ENV)/bin/python3 space-diner.py

.PHONY: build
build:
	$(VIRTUAL_ENV)/bin/pyinstaller space-diner.py
	rm dist/space-diner/levels/
	cp -r levels/ dist/space-diner/
