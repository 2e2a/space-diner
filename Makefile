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

.PHONY: update
update:
	$(VIRTUAL_ENV)/bin/python3 -m pip install --upgrade --upgrade-strategy eager -r requirements-dev.txt
	$(VIRTUAL_ENV)/bin/python3 -m pip freeze > requirements.txt

.PHONY: run
run:
	TODO

.PHONY: pull
pull:
	git pull

.PHONY: deploy
deploy: pull install

.PHONY: fixvenv
fixvenv:
	rm -r $(VIRTUAL_ENV)
	python3 -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python3 -m pip install -r requirements.txt
