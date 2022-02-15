bl_info = {
	"name": "Homeomorphic avatar creator",
	"description": "Homeomorphic avatar creation tools",
	"author": "Martin Petersson",
	"version": (0, 0, 1),
	"blender": (2, 92, 2),
	"location": "View3D",
	"warning": "",
	"wiki_url": "",
	"category": "Avatars"
}
#dependencies: UVPackmaster 2.5.8

#ISSUE-6:	Solution depends on UVPackmaster 2
#	This should be optional
#	labels: dependency

import bpy
from .properties import *
from .ui import *
from .operators import *
from .preferences import *
from . import logging

from .helpers import pending_classes

from . import materials


# Addon registration
def register():

	for cls in pending_classes:
		bpy.utils.register_class(cls)


	bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)
	#ISSUE-5: We should have a save handler that makes sure that images and other large resources are saved the way we want.
	#	The reasoning here is that if multiple artists need to send a blender file back and forth and the textures are unlikely to change we could rely on a version managing tool for synchronization.
	#	Currently the artists are not using such a tool and this feature will therefore be labelled as future-feature.
	#	Note: `bpy.app.handlers.save_pre.append(...)`  and `load_post` for after loading
	#	labels: future-feature


def unregister():
	del bpy.types.Scene.homeomorphictools
	for cls in pending_classes:
		bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    import os
    os.system("clear")
    register()	