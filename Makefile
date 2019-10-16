.PHONY: install update requirements.txt

install: update

update:
	pip install -U pip
	pip install -U -r requirements.txt

requirements.txt:
	pip freeze | grep -v 0.0.0 > $@

.PHONY: merge release wiki

MERGE  = README.md Makefile .gitignore
MERGE += bloc.ipynb metaL.py metaL.ini test_metaL.py requirements.txt

merge:
	git checkout master
	git checkout ponyatov -- $(MERGE)

wiki:
	rm output_*.svg ; unzip ~/Загрузки/bloc.zip ; rm  ~/Загрузки/bloc.zip ; mv bloc.md Home.md 
