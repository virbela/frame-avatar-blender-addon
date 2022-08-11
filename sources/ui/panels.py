from ast import increment_lineno
import bpy
import functools
from ..properties import *
from ..logging import log_writer as log
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
				bake_targets.operator('frame.clear_bake_targets')


			work_meshes = self.layout.box()
			work_meshes.prop(scene.ui_state, "workflow_work_meshes_visible", text="Work Meshes")
			if scene.ui_state.workflow_work_meshes_visible:
				col = work_meshes.column(align=True)
				col.operator('frame.create_workmeshes_for_all_targets')
				col.operator('frame.create_workmeshes_for_selected_target')
				col = work_meshes.column(align=True)
				col.operator('frame.workmesh_to_shapekey')
				col.operator('frame.all_workmesh_to_shapekey')
				col = work_meshes.column(align=True)
				col.operator('frame.shapekey_to_workmesh')
				col.operator('frame.all_shapekey_to_workmesh')
				col = work_meshes.column(align=True)
				col.operator('frame.update_all_workmeshes')
				col.operator('frame.workmesh_symmetrize')

			atlas_setup = self.layout.box()
			atlas_setup.prop(scene.ui_state, "workflow_texture_atlas_visible", text="Texture Atlas")
			if scene.ui_state.workflow_texture_atlas_visible:
				atlas_setup.prop(HT, 'atlas_size')
				atlas_setup.prop(HT, 'color_percentage')
				h = int(HT.color_percentage * HT.atlas_size / 100)
				atlas_setup.label(text=f'Color Region Height in pixels: {h}')

				atlas_setup.operator('frame.auto_assign_atlas')
				atlas_setup.operator('frame.pack_uv_islands')

			work_materials = self.layout.box()
			work_materials.prop(scene.ui_state, "workflow_work_materials_visible", text="Work Materials")
			if scene.ui_state.workflow_work_materials_visible:
				col = work_materials.column(align=True)
				col.operator('frame.update_all_materials')
				col.operator('frame.update_selected_material')

				work_materials.separator()
				work_materials.operator('frame.select_by_atlas')
				work_materials.prop(HT, 'select_by_atlas_image')

			baking = self.layout.box()
			baking.prop(scene.ui_state, "workflow_baking_visible", text="Baking")
			if scene.ui_state.workflow_baking_visible:
				try:
					bake_scene = require_bake_scene(context)
					selection = [o for o in context.selected_objects]
					col = baking.column(align=True)
					col.prop(bake_scene.cycles, "samples", text="Bake Samples")
					col.prop(bake_scene.render.bake, "margin", text="Bake Margin")
					baking.row(align=True).prop(HT, 'baking_options', expand=True)
					baking.prop_search(HT, 'baking_target_uvmap', selection[0].data, "uv_layers")

					col = baking.column(align=True)
					col.operator('frame.bake_all')
					col.operator('frame.bake_selected_bake_target')
					col.operator('frame.bake_selected_workmeshes')
				except AttributeError as e:
					log.info(e)
					baking.label(text='Please ensure Cycles Render Engine is enabled in the addons list!', icon='ERROR')
			helper_tools = self.layout.box()
			helper_tools.prop(scene.ui_state, "workflow_helpers_visible", text="Helpers")
			if scene.ui_state.workflow_helpers_visible:
				col = helper_tools.column(align=True)
				col.operator('frame.synchronize_uv_to_vertices')
				col.operator('frame.select_objects_by_uv')
				col.operator('frame.synchronize_visibility_to_render')
				col.operator('frame.make_everything_visible')
				col.operator('frame.reset_uv_transforms')
				col.operator('frame.recalculate_normals')

			if is_dev():
				debug = self.layout.box()
				debug.label(text='Debug tools')
				debug.operator('frame.clear_bake_scene')



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
	col = layout.column(align=True)

	col.prop(variant, 'image')
	col.prop_search(variant, 'workmesh', bake_scene, 'objects')
	if variant.workmesh:
		col.prop_search(variant, 'uv_map', variant.workmesh.data, 'uv_layers')
	else:
		col.label(text='Select work mesh to choose UV map')

	#TODO - this should perhaps not be visible?
	col.prop(variant, "intermediate_atlas")
	if variant.intermediate_atlas is None:
		col.label(text=f"Intermediate atlas: (not assigned)", icon='UNLINKED')


class FRAME_PT_batch_bake_targets(frame_panel):
	bl_label = "Bake targets"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):

		if scene := require_work_scene(context):
			HT = scene.homeomorphictools
			bake_scene = require_bake_scene(context)

			row = self.layout.row()

			rows = 3
			if HT.selected_bake_target != -1:
				rows = 5

			row.template_list('FRAME_UL_bake_targets', '', HT,  'bake_target_collection', HT, 'selected_bake_target', rows=rows)
			col = row.column(align=True)
			col.operator('frame.add_bake_target', icon='ADD', text='')
			col.operator('frame.remove_bake_target', icon='REMOVE', text='')
			col.separator()
			col.operator('frame.show_selected_bt', icon='EDITMODE_HLT', text='')
			col.operator('frame.clear_bake_targets', icon='X', text='')

			if HT.selected_bake_target != -1:
				et = HT.bake_target_collection[HT.selected_bake_target]

				self.layout.prop_search(et, "source_object", scene, "objects")

				if obj := et.source_object:
					if obj.data.shape_keys:
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


class FRAME_PT_effects(frame_panel):
	bl_label = "Effects"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		ob = context.object
		if not ob or ob.type != 'MESH':
			return 

		if scene := require_work_scene(context):
			HT = scene.homeomorphictools
			self.layout.template_list('FRAME_UL_effects', '', HT, 'effect_collection', HT, 'selected_effect')
			effect_actions = self.layout.row(align=True)
			effect_actions.operator('frame.add_effect')
			effect_actions.operator('frame.remove_effect')

			if HT.selected_effect != -1:
				et = HT.effect_collection[HT.selected_effect]
				self.layout.prop(et, "type")

				key = ob.data.shape_keys
				if et.type == 'POSITION':
					for idx, pos in enumerate(et.positions):
						box = self.layout.box()
						row = box.row()
						row.prop_search(pos, "parent_shapekey", key, "key_blocks", text="")
						row.label(icon='TRIA_RIGHT')
						row.prop_search(pos, "effect_shapekey", key, "key_blocks", text="")
						row.operator("frame.remove_position_effect", icon="X", text="").index = idx
					self.layout.operator("frame.add_position_effect")

				elif et.type == 'COLOR':
					for idx, col in enumerate(et.colors):
						box = self.layout.box()
						row = box.row()
						row.prop_search(col, "shape", key, "key_blocks", text="")
						row.label(icon='TRIA_RIGHT')
						row.prop(col, "color", text="")
						row.operator("frame.remove_color_effect", icon="X", text="").index = idx
						box.prop_search(col, "vert_group", ob, "vertex_groups", text="")
					self.layout.operator("frame.add_color_effect")


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
