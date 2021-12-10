distribution_name = frame-avatar-blender-addon
module_name = frame_avatar_addon

#For not printing the commands - should later have a verbosity flag for this
QUIET_MODE = @

distribution/$(distribution_name).zip: $(wildcard sources/*.py)
	cd distribution && \
	ln -fs ../sources $(module_name) && \
	zip -r $(distribution_name).zip $(module_name) -x $(module_name)/__pycache__/\* && \
	rm -f $(module_name)

vector_test:
	$(QUIET_MODE) PYTHONPATH=sources python3 tests/vector_math.py

#This may look a bit odd because we are specifying two paths separated by : (colon)
# . (dot is current path, we can then import the addon as a module by importing "sources") and tests/mocking
addon_test:
	$(QUIET_MODE) PYTHONPATH=.:tests/mocking python3 tests/addon.py

test: vector_test addon_test

#list-actions finds searches for "#WORD" where WORD is any upper case word, followed by an optional colon and then any non character
list-actions:
	$(QUIET_MODE) grep -Prn '#[A-Z-]+:?\W' sources/ --include='*.py' --color=always -A2	#Show two lines after match
	$(QUIET_MODE) grep -Prn '#[A-Z-]+:?\W' docs/ --exclude='*.svg' --color=always -A2	#Show two lines after match

#list-actions finds searches for "#WORD" where WORD is any upper case word, followed by an optional colon and then any non character
list-actions-short:
	$(QUIET_MODE) grep -Prn '#[A-Z-]+:?\W' sources/ --include='*.py' --color=always
	$(QUIET_MODE) grep -Prn '#[A-Z-]+:?\W' docs/ --exclude='*.svg' --color=always

clean:
	rm -f distribution/*


.PHONY: clean vector_test addon_test list-actions list-actions-short
.IGNORE: list-actions list-actions-short