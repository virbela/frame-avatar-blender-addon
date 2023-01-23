import bpy
from ..utils.properties import UV_ISLAND_MODES
from ..utils.helpers import get_homeomorphic_tool_state

#ISSUE: Some collections are referenced in a problematic way
#	Currently we use indices to refer to items in collections but since items can move around (check if this is true) our indices can be wrong.
#	When an index becomes the wrong thing without any error occuring this can confuse the user so we should either use a system with UUID or see if there are another better way of dealing with this problem.
#	labels: needs-research

#TODO - use a similar pattern for the draw call as we use for operators (see contribution note 3)

class FRAME_UL_bake_variants(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		#layout.label(text=item.name, icon='FILE_BLANK')

		if item.image:
			layout.prop(item, 'name', icon_value=item.image.preview.icon_id, text='', emboss=False, translate=False)
		else:
			layout.prop(item, 'name', icon='UNLINKED', text='', emboss=False, translate=False)


class FRAME_UL_bake_targets(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		if item.bake_mode == 'UV_BM_MIRRORED':
			if target_item := data.bake_target_collection[item.mirror_source]:
				#TODO - we should have a function that automatically fixes index out of range issues in case we lose the reference.
				layout.prop(item, 'name', icon=UV_ISLAND_MODES.members[target_item.uv_mode].icon, text='', emboss=False, translate=False)
				return

		layout.prop(item, 'name', icon=UV_ISLAND_MODES.members[item.uv_mode].icon, text='', emboss=False, translate=False)


class FRAME_UL_bake_groups(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.prop(item, 'name', icon='UNLINKED', text='', emboss=False, translate=False)

class FRAME_UL_bake_group_members(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		if ht := get_homeomorphic_tool_state(context):	#contibution note 2
			if item.target < len(ht.bake_target_collection):
				if target := ht.bake_target_collection[item.target]:
					layout.prop(target, 'name', icon=UV_ISLAND_MODES.members[target.uv_mode].icon, text='', emboss=False, translate=False)
				else:
					layout.label(icon='UNLINKED', text=item.target)
			else:
				layout.label(icon='UNLINKED', text='No target')


class FRAME_UL_bake_target_mirrors(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

		if ht := get_homeomorphic_tool_state(context):	#contribution note 2
			row = layout.row()

			def na(txt):
				'This is a helper function that will say (Not assigned) if the string is empty but otherwise indicate the contents but also convey it is a broken link'

				if txt:
					return f'`{txt}` N/A'
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


class FRAME_UL_effects(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		layout.prop(item, 'name', icon="FORCE_TURBULENCE", text='', emboss=False, translate=False)
