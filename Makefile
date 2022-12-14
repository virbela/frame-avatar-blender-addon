TAG := $(shell git describe --tags --abbrev=0)

test:
	@python tests/__main__.py

release:
	@python scripts/makedist.py $(TAG)
