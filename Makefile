.PHONY: install update requirements.txt

install: update

update:
	pip install -U pip
	pip install -U -r requirements.txt

requirements.txt:
	pip freeze | grep -v 0.0.0 > $@
