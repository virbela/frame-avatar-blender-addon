# frame-avatar-blender-addon
Blender Addon Providing Frame Avatar Tooling

# Installation
Go into Edit > Preferences > Addons > install
Then select `distribution/frame-avatar-blender-addon.zip`

# Developing

## Updating distribution
Run GNU Make on `Makefile`.

Shell command:
```bash
make
```

### Details
This can be done by typing `make` in the root directory of this repository (assuming `make` and `zip` is installed).
If the `sources/*.py` files are newer than `distribution/frame-avatar-blender-addon.zip` make will create a zip archive with the following contents
```
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  2021-10-25 09:25   frame_avatar_addon/
      575  2021-10-25 09:09   frame_avatar_addon/mesh_utilities.py
    27277  2021-10-25 09:09   frame_avatar_addon/__init__.py
---------                     -------
    27852                     3 files
```

## Direct modification of installed addon (linux)
By first uninstalling the addon in blender one can use the working copy of `sources` instead.

Find the installation directory for addons and change directory to it.
Example:
```bash
cd /home/user/.config/blender/2.93/scripts/addons
```

Create a symlink in that directory to the `sources` directory like so
```bash
ln -s /path/to/this/repo/sources frame_avatar_addon
```
Note that additional measures has to be taken for proper reload of such modules in blender and this is not covered here.

### Example of reloading a module using interactive python console in blender
```pycon
>>> import importlib
>>> import frame_avatar_addon.mesh_utilities
>>> importlib.reload(frame_avatar_addon.mesh_utilities)
<module 'frame_avatar_addon.mesh_utilities' from '/home/user/.config/blender/2.93/scripts/addons/frame_avatar_addon/mesh_utilities.py'>
```