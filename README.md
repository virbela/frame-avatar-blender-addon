# FABA(Frame Avatar Blender Addon)
Blender Addon Providing Frame Avatar Tooling

# Installation
Go into Edit > Preferences > Addons > install
Then select `frame-avatar-addon.zip`

# Developing
>Ensure you have [python](https://www.python.org/downloads/) and the [bpy](https://pypi.org/project/bpy/) package installed.

1. Creating a new release
```bash
make release
```

2. Running unit tests
```bash
make test
```

3. Local dev

Install [ScriptWatcher](https://github.com/wisaac407/blender-script-watcher) and point it to the `__init__.py` file in the source directory. Your changes will be automatically reloaded in blender when you save a file in the addon.

4. Debugging

Edit the file `scripts/debug.py` to call the addon operator that needs inspection, set a breakpoint and in VScode, start the debugger  by pressing 
`F5`. 