import bpy
from ..properties import *
from ..helpers import pending_classes, get_homeomorphic_tool_state

#PROBLEM - I (Mikael) messed up at bit in how we handle the unique IDs for collections and need to fix that up properly.

#TODO - use a similar pattern for the draw call as we use for operators (see contribution note 3)

class frame_ui_list(bpy.types.UIList):
	#contribution note 6B
	def __init_subclass__(cls):
		pending_classes.append(cls)

class FRAME_UL_bake_variants(frame_ui_list):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		#layout.label(text=item.name, icon='FILE_BLANK')

		if img := bpy.data.images.get(item.image):
			layout.prop(item, 'name', icon_value=img.preview.icon_id, text='', emboss=False, translate=False)
		else:
			layout.prop(item, 'name', icon='UNLINKED', text='', emboss=False, translate=False)


class FRAME_UL_bake_targets(frame_ui_list):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.prop(item, 'name', icon=UV_ISLAND_MODES.members[item.uv_mode].icon, text='', emboss=False, translate=False)


class FRAME_UL_bake_target_mirrors(frame_ui_list):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

		if ht := get_homeomorphic_tool_state(context):	#contribution note 2
			row = layout.row()

			def na(txt):
				'This is a helper function that will say (Not assigned) if the string is empty but otherwise indicate the contents but also convey it is a broken link'

				if txt:
					return f'`{txt}´ N/A'
				else:
					return '(Not Available)'


			primary = ht.get_bake_target_by_identifier(item.primary)
			secondary = ht.get_bake_target_by_identifier(item.secondary)

			if primary and secondary:
				row.label(text=primary.name, icon=UV_ISLAND_MODES.members[primary.uv_mode].icon)
				row.label(text=secondary.name)
			elif primary:
				row.label(text=primary.name, icon='UNLINKED')
				row.label(text=na(item.secondary))
			elif secondary:
				row.label(text=na(item.primary), icon='UNLINKED')
				row.label(text=secondary.name)
			else:
				row.label(text=na(item.primary), icon='UNLINKED')
				row.label(text=na(item.secondary))
