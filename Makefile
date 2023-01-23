TAG := $(shell git describe --tags --abbrev=0)

test:
	@blender -b -P tests/__main__.py

testpy:
	@python tests/__main__.py

release:
	@python scripts/makedist.py $(TAG)

clean:
	@find . -type f -name "*.blend1" -delete
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete