import bpy
import functools
from ..properties import *
from ..exceptions import InternalError
from ..helpers import require_work_scene, require_bake_scene, pending_classes, is_dev

class frame_panel(bpy.types.Panel):
	#contribution note 6B
	def __init_subclass__(cls):
		pending_classes.append(cls)


if is_dev():
	class FRAME_PT_node_dev_tools(frame_panel):
		bl_label = "Avatar Development Tools"
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
		if scene := require_work_scene(context):
			HT = scene.homeomorphictools

			#TODO - this should point to our documentation for the workflow. This could point to a document that requires the artist to be logged in to that web service (like google docs as an example).
			#We may not want links that anyone can access since the workflow should be considered proprietary
			introduction = self.layout.box()
			introduction.prop(scene.ui_state, "workflow_introduction_visible", text="Introduction")
			if scene.ui_state.workflow_introduction_visible:
				get_help = introduction.operator('wm.url_open', text='Help')
				get_help.url = 'http://example.org/'
				introduction.operator('frame.setup_bake_scene')


			bake_targets = self.layout.box()
			bake_targets.prop(scene.ui_state, "workflow_bake_targets_visible", text="Bake Targets")
			if scene.ui_state.workflow_bake_targets_visible:
				bake_targets.operator('frame.create_targets_from_selection')


			work_meshes = self.layout.box()
			work_meshes.prop(scene.ui_state, "workflow_work_meshes_visible", text="Work Meshes")
			if scene.ui_state.workflow_work_meshes_visible:
				work_meshes.operator('frame.create_workmeshes_for_all_targets')
				work_meshes.operator('frame.create_workmeshes_for_selected_target')
				# TODO(ranjian0)
				# work_meshes.operator('frame.update_selected_workmesh_all_shapekeys')
				# work_meshes.operator('frame.update_selected_workmesh_active_shapekey')

			atlas_setup = self.layout.box()
			atlas_setup.prop(scene.ui_state, "workflow_texture_atlas_visible", text="Texture Atlas")
			if scene.ui_state.workflow_texture_atlas_visible:
				atlas_setup.prop(HT, 'atlas_size')
				atlas_setup.prop(HT, 'color_percentage')
				h = int(HT.color_percentage * HT.atlas_size / 100)
				atlas_setup.label(text=f'Height in pixels: {h}')

				atlas_setup.operator('frame.auto_assign_atlas')
				atlas_setup.operator('frame.pack_uv_islands')

			work_materials = self.layout.box()
			work_materials.prop(scene.ui_state, "workflow_work_materials_visible", text="Work Materials")
			if scene.ui_state.workflow_work_materials_visible:
				work_materials.operator('frame.update_all_materials')
				work_materials.operator('frame.update_selected_material')
				# TODO(ranjian0) Fix
				# work_materials.operator('frame.switch_to_bake_material')
				# work_materials.operator('frame.switch_to_preview_material')

				work_materials.separator()
				work_materials.operator('frame.select_by_atlas')
				work_materials.prop(HT, 'select_by_atlas_image')

			baking = self.layout.box()
			baking.prop(scene.ui_state, "workflow_baking_visible", text="Baking")
			if scene.ui_state.workflow_baking_visible:
				try:
					bake_scene = require_bake_scene(context)
					baking.prop(bake_scene.cycles, "samples", text="Bake Samples")
					baking.prop(bake_scene.render.bake, "margin", text="Bake Margin")
					baking.operator('frame.bake_all')
					baking.operator('frame.bake_selected_bake_target')
					baking.operator('frame.bake_selected_workmeshes')
				except AttributeError:
					baking.label(text='Please ensure Cycles Render Engine is enabled in the addons list!', icon='ERROR')
			helper_tools = self.layout.box()
			helper_tools.prop(scene.ui_state, "workflow_helpers_visible", text="Helpers")
			if scene.ui_state.workflow_helpers_visible:
				helper_tools.operator('frame.synchronize_uv_to_vertices')
				helper_tools.operator('frame.select_objects_by_uv')
				helper_tools.operator('frame.synchronize_visibility_to_render')
				helper_tools.operator('frame.make_everything_visible')
				helper_tools.operator('frame.reset_uv_transforms')
				helper_tools.operator('frame.recalculate_normals')

			if is_dev():
				debug = self.layout.box()
				debug.label(text='Debug tools')
				debug.operator('frame.clear_bake_scene')
				debug.operator('frame.clear_bake_targets')



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


def draw_variant(layout, variant, bake_scene):
	layout.prop(variant, 'image')

	layout.prop_search(variant, 'workmesh', bake_scene, 'objects')
	if variant.workmesh:
		layout.prop_search(variant, 'uv_map', variant.workmesh.data, 'uv_layers')
	else:
		layout.label(text='Select work mesh to choose UV map')

	#TODO - this should perhaps not be visible?
	if variant.intermediate_atlas is None:
		layout.label(text=f"Intermediate atlas: (not assigned)", icon='UNLINKED')
	else:
		if preview := variant.intermediate_atlas.preview:
			layout.label(text=f"Intermediate atlas: {variant.intermediate_atlas.name}", icon_value=preview.icon_id)
		else:
			layout.label(text=f"Intermediate atlas: {variant.intermediate_atlas.name}", icon='FILE_IMAGE')


class FRAME_PT_batch_bake_targets(frame_panel):
	bl_label = "Bake targets"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):

		if scene := require_work_scene(context):
			HT = scene.homeomorphictools
			bake_scene = require_bake_scene(context)

			self.layout.template_list('FRAME_UL_bake_targets', '', HT,  'bake_target_collection', HT, 'selected_bake_target')

			bake_target_actions = self.layout.row(align=True)
			bake_target_actions.operator('frame.add_bake_target')
			bake_target_actions.operator('frame.remove_bake_target')

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
					self.layout.prop(et, 'uv_area_weight', slider=True)

					variants = self.layout.box()
					variants.prop(et, 'multi_variants')

					if et.multi_variants:
						variants.template_list('FRAME_UL_bake_variants', '', et, 'variant_collection', et, 'selected_variant')

						variant_actions = variants.row(align=True)
						variant_actions.operator('frame.add_bake_target_variant')
						variant_actions.operator('frame.remove_bake_target_variant')

						if et.selected_variant != -1:
							var = et.variant_collection[et.selected_variant]
							draw_variant(variants, var, bake_scene)

					else:	# draw the first entry only
						if len(et.variant_collection) == 0:
							variants.label(text='Please revalidate bake target')
						else:
							var = et.variant_collection[0]
							draw_variant(variants, var, bake_scene)

					self.layout.prop(et, 'uv_mode')

					if et.uv_mode == 'UV_IM_FROZEN':
						self.layout.prop(et, 'atlas')

				elif et.bake_mode == 'UV_BM_MIRRORED':
					pass	#TODO
				else:
					raise InternalError(f'et.bake_mode set to unsupported value {et.bake_mode}')

# TODO(ranjian0) Take bake groups into account
# class FRAME_PT_bake_groups(frame_panel):
# 	bl_label = "Bake groups"
# 	bl_space_type = 'VIEW_3D'
# 	bl_region_type = 'UI'
# 	bl_category = "Avatar"

# 	def draw(self, context):

# 		if scene := require_work_scene(context):
# 			HT = scene.homeomorphictools
# 			bake_scene = require_bake_scene(context)

# 			self.layout.template_list('FRAME_UL_bake_groups', '', HT, 'bake_group_collection', HT, 'selected_bake_group')
# 			bake_group_actions = self.layout.row(align=True)
# 			bake_group_actions.operator('frame.add_bake_group')
# 			bake_group_actions.operator('frame.remove_bake_group')

# 			if selected_group := HT.get_selected_bake_group():
# 				group = self.layout.box()
# 				group.label(text='Bake group members')
# 				group.template_list('FRAME_UL_bake_group_members', '', selected_group, 'members', selected_group, 'selected_member')
# 				group_actions = group.row(align=True)
# 				group_actions.operator('frame.add_bake_group_member')
# 				group_actions.operator('frame.remove_bake_group_member')


class FRAME_PT_effects(frame_panel):
	bl_label = "Effects"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		ob = context.object
		if not ob:
			return 

		if scene := require_work_scene(context):
			HT = scene.homeomorphictools
			self.layout.template_list('FRAME_UL_effects', '', HT, 'effect_collection', HT, 'selected_effect')
			effect_actions = self.layout.row(align=True)
			effect_actions.operator('frame.add_effect')
			effect_actions.operator('frame.remove_effect')

			if HT.selected_effect != -1:
				key = ob.data.shape_keys
				if key:
					et = HT.effect_collection[HT.selected_effect]
					self.layout.prop_search(et, "parent_shapekey", key, "key_blocks")
					self.layout.prop_search(et, "effect_shapekey", key, "key_blocks")


class FRAME_PT_export(frame_panel):
	bl_label = "Export"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if scene := require_work_scene(context):
			HT = scene.homeomorphictools
			self.layout.prop(HT, "export_atlas")
			self.layout.prop(HT, "export_glb")
			self.layout.prop(HT, "export_animation")
			self.layout.prop(HT, "denoise")
		self.layout.operator("frame.export")
