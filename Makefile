metal: bin/python metaL.py
	./$^

test:
	py.test -v test_metaL.py

.PHONY: install update requirements.txt

install: update

update:
	pip install -U pip
	pip install -U -r requirements.txt
	$(MAKE) requirements.txt

requirements.txt:
	pip freeze | grep -v 0.0.0 > $@

.PHONY: merge release wiki

MERGE  = README.md Makefile .gitignore
MERGE += bloc.ipynb metaL.py metaL.ini test_metaL.py requirements.txt

merge:
	git checkout master
	git checkout ponyatov -- $(MERGE)

NOW = $(shell date +%y%m%d)
REL = $(shell git rev-parse --short=4 HEAD)
release:
	-git tag $(NOW)-$(REL)
	git push -v ; git push -v --tags
	git checkout ponyatov

wiki:
	rm output_*.svg ; unzip ~/Загрузки/bloc.zip ; rm  ~/Загрузки/bloc.zip ; mv bloc.md Home.md 
