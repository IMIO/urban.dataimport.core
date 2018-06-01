#!/usr/bin/make
#

options =

all: run

.PHONY: bootstrap
bootstrap:
	virtualenv -p python3 .
	./bin/python bootstrap.py

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 60

.PHONY: run
run:
	if ! test -f bin/ton_script;then make buildout;fi
	bin/ton_script acropole_example.cfg

.PHONY: cleanall
cleanall:
	rm -fr bin/instance1 develop-eggs downloads eggs parts .installed.cfg

