module_name = frame_avatar_addon
distribution_name = frame-avatar-blender-addon

#For not printing the commands - should later have a verbosity flag for this
QUIET_MODE = @

distribution/$(distribution_name).zip: $(wildcard sources/*.py)
	ln -fs ./sources $(module_name) && \
	zip -r $(distribution_name).zip $(module_name) -x $(module_name)/*.pyc && \
	rm -f $(module_name)


#This may look a bit odd because we are specifying two paths separated by : (colon)
# . (dot is current path, we can then import the addon as a module by importing "sources") and tests/mocking
addon_test:
	$(QUIET_MODE) PYTHONPATH=.:tests/mocking /usr/bin/python3 tests/addon.py

test: addon_test

#list-actions finds searches for "#WORD" where WORD is any upper case word, followed by an optional colon and then any non character
list-actions:
	$(QUIET_MODE) grep -Prn "#[A-Z-_]+:?(?:\W|$$)" sources/ --include='*.py' --color=always -A2	#Show two lines after match
	$(QUIET_MODE) grep -Prn "#[A-Z-_]+:?(?:\W|$$)" docs/ --exclude='*.svg' --color=always -A2	#Show two lines after match

#list-actions finds searches for "#WORD" where WORD is any upper case word, followed by an optional colon and then any non character
list-actions-short:
	$(QUIET_MODE) grep -Prn "#[A-Z-_]+:?(?:\W|$$)" sources/ --include='*.py' --color=always
	$(QUIET_MODE) grep -Prn "#[A-Z-_]+:?(?:\W|$$)" docs/ --exclude='*.svg' --color=always

#Note that this is unlikely to work on windows but at some point we could look into fixing that
#There is both problems with how we deal with paths and that windows have a different way of making symlinks that require special ntfs tools (could be wrong on this, was a while)
install-development-version:
	$(QUIET_MODE) rm -f .addon_path
	$(QUIET_MODE) blender --background --python scripts/get_addon_path.py -- .addon_path
	$(QUIET_MODE) mkdir -p `cat .addon_path`
	$(QUIET_MODE) ln -fs "$(shell pwd)/sources" "`cat .addon_path`/$(module_name)"

clean:
	rm -f distribution/*


.PHONY: clean addon_test list-actions list-actions-short install-development-version
.IGNORE: list-actions list-actions-short