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
	# global original_inspect_getsourcelines
	#NOTE why was that? ↑

	for cls in pending_classes:
		bpy.utils.register_class(cls)


	#CLEAN tests under here
	#print(dir(BakeTarget.bl_rna))
	#print(BakeTarget.bl_rna.properties['mirror_source'])
	#BakeTarget.bl_rna.properties['mirror_source'] = bpy.props.PointerProperty(name='Bake target used for mirror', type=BakeTarget.bl_rna.rna_type)
	#print(BakeTarget.bl_rna.properties['mirror_source'])
	#print(bpy.types.PointerProperty(BakeTarget.bl_rna))


	#BakeTarget.bl_rna.properties['mirror_source'] =  bpy.props.PointerProperty(name='bake ref', type=BakeTarget)()  # bpy.types.PointerProperty(BakeTarget.bl_rna)

	bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)
	#TODO		bpy.app.handlers.save_pre.append(...)    #and load_post

def unregister():
	del bpy.types.Scene.homeomorphictools
	for cls in pending_classes:
		bpy.utils.unregister_class(cls)
