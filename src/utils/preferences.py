import bpy
from bpy.types import Context
from .helpers import pending_classes, register_class

@register_class	#contribution note 6A
class FrameAddonPreferences(bpy.types.AddonPreferences):
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

	def draw(self, context: Context):
		layout = self.layout
		layout.prop(self, 'log_target')
		layout.prop(self, 'glb_export_dir')
		layout.prop(self, 'atlas_export_dir')