bl_info = {
	"name": "Homeomorphic avatar creator",
	"description": "Homeomorphic avatar creation tools",
	"author": "Martin Petersson, Ian Karanja",
	"version": (0, 1, 4),
	"blender": (2, 92, 2),
	"location": "View3D",
	"warning": "",
	"wiki_url": "",
	"category": "Avatars"
}
#dependencies: UVPackmaster 2.5.8

#ISSUE-6:	Solution depends on UVPackmaster 2/3
#	This should be optional
#	labels: dependency

import bpy
from .ui import * 
from .operators import *
from .preferences import *
from .helpers import pending_classes
from .properties import HomeomorphicProperties, UIStateProperty


# Addon registration
def register():
	for cls in pending_classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)
	bpy.types.Scene.ui_state = bpy.props.PointerProperty(type=UIStateProperty)
	#ISSUE-5: We should have a save handler that makes sure that images and other large resources are saved the way we want.
	#	The reasoning here is that if multiple artists need to send a blender file back and forth and the textures are unlikely to change we could rely on a version managing tool for synchronization.
	#	Currently the artists are not using such a tool and this feature will therefore be labelled as future-feature.
	#	Note: `bpy.app.handlers.save_pre.append(...)`  and `load_post` for after loading
	#	labels: future-feature


def unregister():
	del bpy.types.Scene.ui_state
	del bpy.types.Scene.homeomorphictools
	for cls in pending_classes:
		bpy.utils.unregister_class(cls)


if __name__ == '__main__':
	# XXX ScriptWatcher hook for local development
	import os; os.system("cls" if os.name == "nt" else "clear")

	try:
		unregister()
	except:
		pass
	register()	