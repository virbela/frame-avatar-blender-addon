import bpy
from .helpers import pending_classes, register_class

@register_class	#contribution note 6A
class FrameAddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	log_target: 					bpy.props.StringProperty(name='Target filename for addon log', subtype='FILE_NAME', default="fabalog")
	custom_export_dir: 				bpy.props.StringProperty(name='Folder to use for glb export (default is current blendfile folder).', subtype='DIR_PATH')
	save_intermediate_atlases: 		bpy.props.BoolProperty()

	def draw(self, context):
		layout = self.layout
		layout.label(text="Frame Addon Preferences")
		layout.prop(self, 'log_target')
		layout.prop(self, 'custom_export_dir')
		layout.prop(self, 'save_intermediate_atlases')