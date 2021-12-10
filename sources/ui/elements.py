import bpy
from .. import utilities
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

		if HT := get_homeomorphic_tool_state(context):	#contribution note 2
			row = layout.row()

			primary = HT.bake_target_collection.get(item.primary)
			secondary = HT.bake_target_collection.get(item.secondary)

			print(primary)

			if primary and secondary:
				row.label(text=primary.name, icon=UV_ISLAND_MODES.members[primary.uv_mode].icon)
				row.label(text=secondary.name)
			elif primary:
				row.label(text=primary.name, icon='UNLINKED')
				row.label(text='(Not assigned')
			elif secondary:
				row.label(text='(Not assigned', icon='UNLINKED')
				row.label(text=secondary.name)
			else:
				row.label(text='(Not assigned)', icon='UNLINKED')
				row.label(text='(Not assigned)')
