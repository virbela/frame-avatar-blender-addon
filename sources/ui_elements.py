import bpy
from . import utilities
from .properties import *

@utilities.register_class
class FRAME_UL_bake_targets(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.label(text=item.description, icon=UV_ISLAND_MODES.members[item.uv_mode].icon)

		#Note - there are multipl layout types as shown in this example
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

		#primary = item.primary

		#print(list(HT.bake_target_collection))

		if primary:
			row.label(text=item.primary or '???', icon=UV_ISLAND_MODES.members[primary.uv_mode].icon)
			row.label(text=item.secondary or '???')
		else:
			row.label(text=item.primary or '???', icon='UNLINKED')
			row.label(text=item.secondary or '???')


