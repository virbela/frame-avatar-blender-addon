import bpy
from . import utilities


@utilities.register_class
class FrameAddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	log_target: bpy.props.StringProperty(name='Target filename for addon log', subtype='FILE_NAME')


	def draw(self, context):
		layout = self.layout
		layout.label(text="Frame Addon Preferences")
		layout.prop(self, 'log_target')