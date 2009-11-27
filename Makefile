
# Simple Makefile for some common tasks. This will get
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

clean:
	find . -name "*.pyc" |xargs rm
	rm -r dist
	rm -r tiddlyweb_plugins.egg-info

dist:
	python setup.py sdist

upload:
	python setup.py sdist upload
	scp -P 8022 dist/tiddlywebplugins*.gz cdent@tiddlyweb.peermore.com:public_html/tiddlyweb.peermore.com/dist
