import bpy
from ..properties import *
from ..helpers import get_work_scene, get_bake_scene, pending_classes
from .. import operators
import functools


import textwrap

def textlines(txt):
	return textwrap.dedent(txt).strip('\r\n\t ').split('\n')

class frame_panel(bpy.types.Panel):
	#contribution note 6B
	def __init_subclass__(cls):
		pending_classes.append(cls)


#TODO - this should be guarded by a devmode boolean
class FRAME_PT_node_dev_tools(frame_panel):
	bl_label = "Development Tools"
	bl_space_type = 'NODE_EDITOR'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		self.layout.operator('frame.create_node_script')



class FRAME_PT_workflow(frame_panel):
	bl_label = "Workflow"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			introduction = self.layout.box()
			introduction.label(text='Introduction')
			#TODO - this should point to our documentation for the workflow. This could point to a document that requires the artist to be logged in to that web service (like google docs as an example).
			#We may not want links that anyone can access since the workflow should be considered proprietary
			get_help = introduction.operator('wm.url_open', text='Help')
			get_help.url = 'http://example.org/'
			introduction.operator('frame.setup_bake_scene')


			bake_targets = self.layout.box()
			bake_targets.label(text='Bake targets')
			bake_targets.operator('frame.create_targets_from_selection')
			bake_targets.operator('frame.validate_targets')


			work_meshes = self.layout.box()
			work_meshes.label(text='Work meshes')
			work_meshes.operator('frame.create_workmeshes_for_all_targets')
			work_meshes.operator('frame.create_workmeshes_for_selected_target')
			work_meshes.operator('frame.update_selected_workmesh_all_shapekeys')
			work_meshes.operator('frame.update_selected_workmesh_active_shapekey')


			atlas_setup = self.layout.box()
			atlas_setup.label(text='Texture atlas')
			atlas_setup.operator('frame.auto_assign_atlas')
			atlas_setup.operator('frame.pack_uv_islands')


			work_materials = self.layout.box()
			work_materials.label(text='Work materials')
			work_materials.operator('frame.update_selected_material')
			work_materials.operator('frame.update_all_materials')
			work_materials.operator('frame.switch_to_bake_material')
			work_materials.operator('frame.switch_to_preview_material')

			baking = self.layout.box()
			baking.label(text='Baking')
			baking.operator('frame.bake_selected')
			baking.operator('frame.bake_all')

			#TODO - clean this up!

			# self.layout.operator('frame.auto_assign_atlas')
			# self.layout.operator('frame.pack_uv_islands')
			# self.layout.operator('frame.update_baking_scene')
			# self.layout.operator('frame.bake_all')

			# helpers = self.layout.box()
			# helpers.label(text='Extra utilities')
			# helpers.operator('frame.bake_selected')
			# helpers.operator('frame.synchronize_mirrors')


			# materials = self.layout.box()
			# materials.label(text='Materials')
			# materials.operator('frame.switch_to_bake_material')
			# materials.operator('frame.switch_to_preview_material')


			#TODO - remove or make conditional
			debug = self.layout.box()
			debug.label(text='Debug tools')
			debug.operator('frame.place_holder_for_experiments')
			debug.operator('frame.clear_bake_scene')
			debug.operator('frame.clear_bake_targets')




class FRAME_PT_painting(frame_panel):
	bl_label = "Texture painting"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			self.layout.prop(HT, 'painting_size')


class FRAME_PT_uv_packing(frame_panel):
	bl_label = "Texture atlas"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			self.layout.prop(HT, 'atlas_size')
			self.layout.prop(HT, 'color_percentage')
			h = int(HT.color_percentage * HT.atlas_size / 100)
			self.layout.label(text=f'Height in pixels: {h}')



class template_expandable_section:
	_EXPANDED_ICON = 'TRIA_DOWN'
	_COLLAPSED_ICON = 'TRIA_RIGHT'

	def __init__(self, layout, data, title, expanded_property):
		self._layout = layout.box()
		self._state = getattr(data, expanded_property)
		self._layout.prop(data, expanded_property, text=title, icon=self._EXPANDED_ICON if self._state else self._COLLAPSED_ICON)

	def __getattr__(self, key):
		if self._state:
			return functools.partial(getattr(self._layout, key))
		else:
			return lambda *a, **n: None	#This is a dummy function so when this template is hidden nothing is displayed




class FRAME_PT_batch_bake_targets(frame_panel):
	bl_label = "Bake targets"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):

		if scene := get_work_scene(context):
			HT = scene.homeomorphictools
			bake_scene = get_bake_scene(context)

			self.layout.template_list('FRAME_UL_bake_targets', '', HT,  'bake_target_collection', HT, 'selected_bake_target')

			bake_target_actions = self.layout.row(align=True)
			bake_target_actions.operator('frame.add_bake_target')
			bake_target_actions.operator('frame.remove_bake_target')
			#bake_target_actions.operator('frame.show_selected_bt')	#LATER


			#TODO - document the reasoning behind all this
			#TODO - divy up this into a few functions to make it less messy
			if HT.selected_bake_target != -1:
				et = HT.bake_target_collection[HT.selected_bake_target]

				self.layout.prop_search(et, "source_object", scene, "objects")

				if obj := et.source_object:
					if shape_keys := obj.data.shape_keys:
						self.layout.prop_search(et, "shape_key_name", obj.data.shape_keys, "key_blocks")



				self.layout.prop(et, 'bake_mode')

				if et.bake_mode == 'UV_BM_REGULAR':

					self.layout.prop(et, 'uv_area_weight')

					variants = self.layout.box()
					variants.prop(et, 'multi_variants')

					if et.multi_variants:
						variants.template_list('FRAME_UL_bake_variants', '', et, 'variant_collection', et, 'selected_variant')

						variant_actions = variants.row(align=True)
						variant_actions.operator('frame.add_bake_target_variant')
						variant_actions.operator('frame.remove_bake_target_variant')

						if et.selected_variant != -1:
							var = et.variant_collection[et.selected_variant]
							variants.prop(var, 'image')

							variants.prop_search(var, 'workmesh', bake_scene, 'objects')
							if var.workmesh:
								variants.prop_search(var, 'uv_map', var.workmesh.data, 'uv_layers')
							else:
								variants.label(text='Select work mesh to choose UV map')


					else:	# draw the first entry only
						if len(et.variant_collection) == 0:
							variants.label(text='Please revalidate bake target')
						else:
							var = et.variant_collection[0]
							variants.prop_search(var, 'image', bpy.data, 'images')

							variants.prop_search(var, 'workmesh', bake_scene, 'objects')
							if var.workmesh:
								variants.prop_search(var, 'uv_map', var.workmesh.data, 'uv_layers')
							else:
								variants.label(text='Select work mesh to choose UV map')



					self.layout.prop(et, 'uv_mode')

					if et.uv_mode == 'UV_IM_FROZEN':
						self.layout.prop(et, 'atlas')
						#TODO - decide what to do here
						# if et.workmesh:
						# 	#self.layout.prop_search(et, 'uv_map', obj.data, 'uv_layers')
						# 	self.layout.prop(et, 'uv_target_channel')
						# else:
						# 	self.layout.label(text=f"UV set: (No object)")
					else:

						if et.atlas is None:
							self.layout.label(text=f"Atlas: (not assigned)", icon='UNLINKED')
						else:
							self.layout.label(text=f"Atlas: {et.atlas.name}", icon_value=et.atlas.preview.icon_id)


						#self.layout.label(text=f"UV set: {et.uv_map or '(not assigned)'}")
						self.layout.label(text=f"UV target: {UV_TARGET_CHANNEL.members[et.uv_target_channel].name}", icon=UV_TARGET_CHANNEL.members[et.uv_target_channel].icon)



				elif et.bake_mode == 'UV_BM_MIRRORED':
					#self.layout.prop_search(et, 'mirror_source', HT, 'bake_target_collection')
					#self.layout.prop(et, 'mirror_source')

					pass	#TODO
					#BUG - when showing the FRAME_UL_bake_targets list in two places we get trouble with shared state
					# uv_mirror_options = template_expandable_section(self.layout, et, 'UV mirror options', 'uv_mirror_options_expanded')
					# uv_mirror_options.prop(et, 'uv_mirror_axis')
					# uv_mirror_options.label(text='Source of mirror')
					# uv_mirror_options.template_list('FRAME_UL_bake_targets', '', HT,  'bake_target_collection', et, 'mirror_source')


					#self.layout.prop(et, 'geom_mirror_axis')		#MAYBE-LATER
				else:
					raise InternalError(f'et.bake_mode set to unsupported value {et.bake_mode}')








			#TODO - add button for synchronizing primary → secondary (where? here or utils?)
			# mirrors = self.layout.box()
			# mirrors.label(text='Mirrored bake targets')
			# mirrors.template_list('FRAME_UL_bake_target_mirrors', '', HT,  'bake_target_mirror_collection', HT, 'selected_bake_target_mirror')

			# bake_target_actions = mirrors.row(align=True)
			# bake_target_actions.operator('frame.add_bake_target_mirror')
			# bake_target_actions.operator('frame.remove_bake_target_mirror')

			# if HT.selected_bake_target_mirror != -1:
			# 	tm = HT.bake_target_mirror_collection[HT.selected_bake_target_mirror]
			# 	row = mirrors.row()
			# 	row.operator('frame.set_bake_mirror_primary')
			# 	row.operator('frame.set_bake_mirror_secondary')


			# advanced = self.layout.box()
			# advanced.label(text='Create from shapekeys')
			# advanced.prop_search(HT, 'source_object', scene, 'objects')
			# advanced.operator('frame.create_bake_targets_from_shapekeys')

class FRAME_PT_bake_groups(frame_panel):
	bl_label = "Bake groups"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):

		if scene := get_work_scene(context):
			HT = scene.homeomorphictools
			bake_scene = get_bake_scene(context)

			self.layout.template_list('FRAME_UL_bake_groups', '', HT, 'bake_group_collection', HT, 'selected_bake_group')
			bake_group_actions = self.layout.row(align=True)
			bake_group_actions.operator('frame.add_bake_group')
			bake_group_actions.operator('frame.remove_bake_group')

			if selected_group := HT.get_selected_bake_group():
				group = self.layout.box()
				group.label(text='Bake group members')
				group.template_list('FRAME_UL_bake_group_members', '', selected_group, 'members', selected_group, 'selected_member')
				group_actions = group.row(align=True)
				group_actions.operator('frame.add_bake_group_member')
				group_actions.operator('frame.remove_bake_group_member')

				#NOTE - Currently we don't allow to change the target afterwards, instead we have to remove and select a differet target and add it.
				# This might be slightly confusing for the user though since it is fairly far between the bake targets and bake groups so we may want to improve this later

				# if selected_group.selected_member != -1:
				# 	selected_member = selected_group.members[selected_group.selected_member]
				# 	self.layout.prop_search(selected_member, 'target', HT, 'bake_target_collection')