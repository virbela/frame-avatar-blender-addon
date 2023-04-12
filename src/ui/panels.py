import bpy

from ..utils.exceptions import InternalError
from ..utils.logging import log_writer as log
from ..utils.helpers import get_homeomorphic_tool_state, require_work_scene, require_bake_scene, is_dev


class FRAME_PT_workflow(bpy.types.Panel):
	bl_label = "Workflow"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		HT = get_homeomorphic_tool_state(context)
		ui_state = context.scene.ui_state

		self.layout.prop(HT, "avatar_mesh")
		self.layout.prop(HT, "avatar_rig")

		#TODO - this should point to our documentation for the workflow. This could point to a document that requires the artist to be logged in to that web service (like google docs as an example).
		#We may not want links that anyone can access since the workflow should be considered proprietary
		introduction = self.layout.box()
		introduction.prop(ui_state, "workflow_introduction_visible", text="Introduction")
		if ui_state.workflow_introduction_visible:
			get_help = introduction.operator('wm.url_open', text='Help')
			get_help.url = 'http://example.org/'
			introduction.operator('frame.setup_bake_scene')


		bake_targets = self.layout.box()
		bake_targets.prop(ui_state, "workflow_bake_targets_visible", text="Bake Targets")
		if ui_state.workflow_bake_targets_visible:
			bake_targets.operator('frame.create_targets_from_avatar_object')
			bake_targets.operator('frame.clear_bake_targets')


		work_meshes = self.layout.box()
		work_meshes.prop(ui_state, "workflow_work_meshes_visible", text="Work Meshes")
		if ui_state.workflow_work_meshes_visible:
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
			work_meshes.label(text="Mirror")
			col = work_meshes.column(align=True)
			col.prop(HT, "mirror_verts_source")
			col.prop(HT, "mirror_verts_target")
			col.operator('frame.mirror_workmesh_verts')


		atlas_setup = self.layout.box()
		atlas_setup.prop(ui_state, "workflow_texture_atlas_visible", text="Texture Atlas")
		if ui_state.workflow_texture_atlas_visible:
			atlas_setup.prop(HT, 'atlas_size')
			atlas_setup.prop(HT, 'color_percentage')
			h = int(HT.color_percentage * HT.atlas_size / 100)
			atlas_setup.label(text=f'Color Region Height in pixels: {h}')

			atlas_setup.operator('frame.auto_assign_atlas')
			atlas_setup.operator('frame.pack_uv_islands')

		work_materials = self.layout.box()
		work_materials.prop(ui_state, "workflow_work_materials_visible", text="Work Materials")
		if ui_state.workflow_work_materials_visible:
			col = work_materials.column(align=True)
			col.operator('frame.update_all_materials')
			col.operator('frame.update_selected_material')

			work_materials.separator()
			col = work_materials.column(align=True)
			col.operator('frame.select_by_atlas')
			col.operator('frame.set_selected_workmesh_atlas')
			work_materials.prop(HT, 'select_by_atlas_image')

		baking = self.layout.box()
		baking.prop(ui_state, "workflow_baking_visible", text="Baking")
		if ui_state.workflow_baking_visible:
			bake_scene = require_bake_scene(context)
			selection = [o for o in context.selected_objects]
			try:
				col = baking.column(align=True)
				col.prop(bake_scene.cycles, "samples", text="Bake Samples")
				col.prop(bake_scene.render.bake, "margin", text="Bake Margin")
			except AttributeError as e:
				log.info(e)
				baking.label(text='Please ensure Cycles Render Engine is enabled in the addons list!', icon='ERROR')

			baking.row(align=True).prop(HT, 'baking_options', expand=True)
			if selection and selection[0].type == 'MESH':
				baking.prop_search(HT, 'baking_target_uvmap', selection[0].data, "uv_layers")

			col = baking.column(align=True)
			col.operator('frame.bake_all')
			col.operator('frame.bake_selected_bake_target')
			if selection:
				col.operator('frame.bake_selected_workmeshes')
			else:
				baking.label(text='Please select a workmesh to bake from one!', icon='INFO')

		helper_tools = self.layout.box()
		helper_tools.prop(ui_state, "workflow_helpers_visible", text="Helpers")
		if ui_state.workflow_helpers_visible:
			col = helper_tools.column(align=True)
			col.operator('frame.reset_uv_transforms')
			col.separator()
			uv_col = col.box().column()
			uv_col.prop(HT, "source_object_uv")
			uv_col.prop(HT, "target_object_uv")
			uv_col.operator('frame.copy_uv_layers')

		if is_dev():
			debug = self.layout.box()
			debug.label(text='Debug tools')
			debug.operator('frame.clear_bake_scene')
			debug.label(text="Bone Animation Viz")
			col = debug.column(align=True)
			col.prop_search(HT, "debug_animation_name", bpy.data, "actions", text="Action")
			op_text = "Stop Animation" if HT.debug_animation_show else "Show Animation"
			debug.operator('frame.debug_bone_animation', text=op_text)


class FRAME_PT_bake_targets(bpy.types.Panel):
	bl_label = "Bake targets"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if HT := get_homeomorphic_tool_state(context):
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
				col.prop(et, "export", toggle=True, text="", icon="EXPORT")

				if obj := HT.avatar_mesh:
					if obj.data.shape_keys:
						self.layout.prop_search(et, "shape_key_name", obj.data.shape_keys, "key_blocks")

				self.layout.prop(et, 'bake_mode', expand=True)
				if et.bake_mode == 'UV_BM_REGULAR':
					self.layout.prop(et, 'uv_mode')
					if et.uv_mode == "UV_IM_NIL":
						return
					if len(et.variant_collection):
						variant = et.variant_collection[0]
						if variant.workmesh:
							self.layout.prop_search(variant, 'uv_map', variant.workmesh.data, 'uv_layers')
						else:
							self.layout.label(text='Select work mesh to choose UV map', icon="ERROR")

						# TODO(ranjian0) Is this used for UV packing really?
						# self.layout.prop(et, 'uv_area_weight', text="UV Area")
						if bake_scene := require_bake_scene(context):
							self.layout.prop_search(variant, 'workmesh', bake_scene, 'objects')
						else:
							self.layout.label("Missing bake scene!", icon="ERROR")
						self.layout.prop(variant, 'image')

						if et.uv_mode == 'UV_IM_FROZEN':
							self.layout.prop(et, 'atlas')
						#TODO - this should perhaps not be visible?
						self.layout.prop(variant, "intermediate_atlas")
						if variant.intermediate_atlas is None:
							self.layout.label(text=f"Intermediate atlas: (not assigned)", icon='UNLINKED')

				elif et.bake_mode == 'UV_BM_MIRRORED':
					pass	#TODO(ranjian0) Show opposite mirror for the current target
				else:
					raise InternalError(f'et.bake_mode set to unsupported value {et.bake_mode}')


class FRAME_PT_effects(bpy.types.Panel):
	bl_label = "Effects"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if HT := get_homeomorphic_tool_state(context):
			ob = HT.avatar_mesh
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


class FRAME_PT_export(bpy.types.Panel):
	bl_label = "Export"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if HT := get_homeomorphic_tool_state(context):
			self.layout.prop(HT, "avatar_type", expand=True)
			self.layout.prop(HT, "export_glb")
			self.layout.prop(HT, "export_atlas")
			if HT.export_atlas:
				sp = self.layout.split(factor=0.05)
				_ = sp.column()
				col = sp.column()
				col.prop(HT, "denoise")


			anim = self.layout.row()
			anim.enabled = HT.avatar_type == "FULLBODY"
			anim.prop(HT, "export_animation")
			if HT.avatar_type == "FULLBODY" and HT.export_animation:
				self.layout.prop(HT, "animation_type", expand=True)
				if not HT.export_animation_actions:
					self.layout.label(text="No actions found!", icon="ERROR")
				sp = self.layout.split(factor=0.05)
				_ = sp.column()
				col = sp.column()
				for ea in sorted(HT.export_animation_actions, key=lambda a: a.name):
					col.prop(ea, "checked", text=ea.name)

				self.layout.prop(HT, "export_animation_actions", expand=True, text="")
		self.layout.operator("frame.export", text="Export")
