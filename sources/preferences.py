import bpy
from .helpers import pending_classes, register_class

@register_class	#contribution note 6A
class FrameAddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	log_target: bpy.props.StringProperty(name='Target filename for addon log', subtype='FILE_NAME')


	def draw(self, context):
		layout = self.layout
		layout.label(text="Frame Addon Preferences")
		layout.prop(self, 'log_target')