.DEFAULT: help

SHELL := /bin/bash
VENV=venv
PYTHON=$(VENV)/bin/python3
PIP=$(VENV)/bin/pip
SHEET_ID='1Ek5cl3SoJbuo5946G6TFyssjISu--8poMg5sQsWmT0w'
RANGE_NAMES='[APP FIREWALL] Timeline 2024.1,[YARA] Timeline 2024.1,[OCA] Timeline 2024.1'
PROJECT_NAMES='App Firewall,Yara project,OCA'
ORGS='nufuturo-ufcg,nufuturo-ufcg,OCA-UFCG'

venv:
	python3 -m venv $(VENV)
	. ./$(VENV)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: venv
	$(PYTHON) __main__.py \
		--sample-sheet-id $(SHEET_ID) \
		--sample-range-names $(RANGE_NAMES) \
		--project-names $(PROJECT_NAMES) \
		--organizations $(ORGS) \

clean:
	rm -rf $(VENV)
	find src/ -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
