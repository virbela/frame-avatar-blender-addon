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

from .properties import *
from .panels import *
from .operators import *
from . import utilities
import bpy

# Addon registration
def register():
	for cls in utilities.pending_classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)

def unregister():
	del bpy.types.Scene.homeomorphictools
	for cls in utilities.pending_classes:
		bpy.utils.unregister_class(cls)
