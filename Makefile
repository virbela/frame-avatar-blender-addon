TAG := $(shell git describe --tags --abbrev=0)

test:
	@blender --window-geometry 0 0 1 1 --no-window-focus -P tests/__main__.py

release:
	@python scripts/makedist.py $(TAG)
