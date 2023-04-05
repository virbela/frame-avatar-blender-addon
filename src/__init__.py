bl_info = {
	"name": "Homeomorphic avatar creator",
	"description": "Homeomorphic avatar creation tools",
	"author": "Martin Petersson, Ian Karanja",
	"version": (0, 2, 1),
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
from bpy.types import Context
from bpy.app.handlers import persistent

from .ui import register_ui, unregister_ui
from .ops import register_ops, unregister_ops
from .utils.helpers import require_work_scene
from .utils.properties import HomeomorphicProperties, UIStateProperty, register_props, unregister_props

class FrameAvatarAddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	log_target: 					bpy.props.StringProperty(name='Log File Name', subtype='FILE_NAME', default="fabalog")
	glb_export_dir: 				bpy.props.StringProperty(
										name='GLB Export Dir',
										description='Folder to use for glb export (default is current blendfile folder).', subtype='DIR_PATH'
									)
	atlas_export_dir: 				bpy.props.StringProperty(
										name='Atlas Export Dir',
										description='Folder to use for atlas export (default is current blendfile folder).', subtype='DIR_PATH'
									)
	npy_export_dir: 				bpy.props.StringProperty(
										name='Npy Export Dir',
										description='Folder to use for animation (.npy) export (default is current blendfile folder).', subtype='DIR_PATH'
									)
	custom_frame_validation:		bpy.props.BoolProperty(
										default=False,
										name='Frame Validation',
										description='Enable validation for the frame avatars. (Frame artists only!)'
									)

	def draw(self, context: Context):
		layout = self.layout
		layout.prop(self, 'log_target')
		layout.prop(self, 'glb_export_dir')
		layout.prop(self, 'atlas_export_dir')
		layout.prop(self, 'npy_export_dir')
		layout.prop(self, 'custom_frame_validation')



# Addon registration
def register():
	# XXX Order Matters
	bpy.utils.register_class(FrameAvatarAddonPreferences)
	register_props()
	register_ops()
	register_ui()

	bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)
	bpy.types.Scene.ui_state = bpy.props.PointerProperty(type=UIStateProperty)
	#ISSUE-5: We should have a save handler that makes sure that images and other large resources are saved the way we want.
	#	The reasoning here is that if multiple artists need to send a blender file back and forth and the textures are unlikely to change we could rely on a version managing tool for synchronization.
	#	Currently the artists are not using such a tool and this feature will therefore be labelled as future-feature.
	#	Note: `bpy.app.handlers.save_pre.append(...)`  and `load_post` for after loading
	#	labels: future-feature

	def set_export_actions():
		context = bpy.context
		if scene := require_work_scene(context):
			HT = scene.homeomorphictools

			eactions = [ea.name for ea in HT.export_animation_actions]
			for action in bpy.data.actions:
				if 'tpose' in action.name.lower() or action.name in eactions:
					continue

				item = HT.export_animation_actions.add()
				item.name = action.name
				item.checked = True

			for idx, eaction in enumerate(HT.export_animation_actions):
				if eaction.name not in [a.name for a in bpy.data.actions]:
					HT.export_animation_actions.remove(idx)
		return 2


	bpy.app.timers.register(set_export_actions, first_interval=1)

	@persistent
	def refresh_timer_on_file_open(dummy):
		if not bpy.app.timers.is_registered(set_export_actions):
			bpy.app.timers.register(set_export_actions, first_interval=1)
	bpy.app.handlers.load_post.append(refresh_timer_on_file_open)


def unregister():
	del bpy.types.Scene.ui_state
	del bpy.types.Scene.homeomorphictools

	unregister_ui()
	unregister_ops()
	unregister_props()
	bpy.utils.unregister_class(FrameAvatarAddonPreferences)


if __name__ == '__main__':
	# XXX ScriptWatcher hook for local development
	import os; os.system("cls" if os.name == "nt" else "clear")

	try:
		unregister()
	except:
		pass
	register()

	from .utils.bone_animation_viewer import view_animation
	view_animation(animation="stand-clap", shapekey_name="Arm_L")