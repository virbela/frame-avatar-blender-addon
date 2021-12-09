import bpy
from .. import utilities
from ..properties import *

#TODO - replace labels with props to allow in place edit

@utilities.register_class
class FRAME_UL_bake_variants(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		#layout.label(text=item.name, icon='FILE_BLANK')


		if img := bpy.data.images.get(item.image):
			layout.prop(item, 'name', icon_value=img.preview.icon_id, text='', emboss=False, translate=False)
		else:
			layout.prop(item, 'name', icon='UNLINKED', text='', emboss=False, translate=False)


#NOTE - we are currently using item.name for bake targets to identify them but we can't change that name right now
#		we should add a way to change the name

@utilities.register_class
class FRAME_UL_bake_targets(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.label(text=item.name, icon=UV_ISLAND_MODES.members[item.uv_mode].icon)

		#NOTE - there are multipl layout types as shown in this example
			# # Make sure your code supports all 3 layout types
			# if self.layout_type in {'DEFAULT', 'COMPACT'}:
			# 	layout.label(text=item.name, icon = 'SOMEICON')

			# elif self.layout_type in {'GRID'}:
			# 	layout.alignment = 'CENTER'
			# 	layout.label(text="", icon = custom_icon)


@utilities.register_class
class FRAME_UL_bake_target_mirrors(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		row = layout.row()

		HT = context.scene.homeomorphictools
		primary = None
		for entry in HT.bake_target_collection:
			if entry.identifier == item.primary:
				primary = entry


		if primary:
			row.label(text=item.primary or '???', icon=UV_ISLAND_MODES.members[primary.uv_mode].icon)
			row.label(text=item.secondary or '???')
		else:
			row.label(text=item.primary or '???', icon='UNLINKED')
			row.label(text=item.secondary or '???')


