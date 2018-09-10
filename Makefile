#!/usr/bin/make
#

options =

all: run

.PHONY: bootstrap
bootstrap:
	virtualenv -p python3.6 .
	bin/pip install -r requirements.txt
	./bin/python3.6 bootstrap.py

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 60

.PHONY: run
run:
	if ! test -f bin/acropole_script;then make buildout;fi
	bin/acropole_script acropole_example.cfg

.PHONY: cleanall
cleanall:
	rm -fr bin develop-eggs downloads eggs parts .installed.cfg share lib
