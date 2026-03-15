PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

.PHONY: setup run init clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

init:
	$(PY) -c "from app import init_db; init_db(); print('DB ready')"

run: init
	$(PY) app.py

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache
