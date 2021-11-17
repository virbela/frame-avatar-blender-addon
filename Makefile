distribution_name = frame-avatar-blender-addon
module_name = frame_avatar_addon


distribution/$(distribution_name).zip: $(wildcard sources/*.py)
	cd distribution && \
	ln -fs ../sources $(module_name) && \
	zip -r $(distribution_name).zip $(module_name) -x $(module_name)/__pycache__/\* && \
	rm -f $(module_name)

test:
	PYTHONPATH=sources python3 tests/vector_math.py

clean:
	rm -f distribution/*

.PHONY: clean test