TAG := $(shell git describe --tags --abbrev=0)

test:
	@python tests/__main__.py

testb:
	@blender --window-geometry 0 0 1 1 --no-window-focus -P tests/__main__.py

release:
	@python scripts/makedist.py $(TAG)

clean:
	@find . -type f -name "*.blend1" -delete
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete