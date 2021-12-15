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
	global original_inspect_getsourcelines
	for cls in pending_classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)

def unregister():
	del bpy.types.Scene.homeomorphictools
	for cls in pending_classes:
		bpy.utils.unregister_class(cls)
