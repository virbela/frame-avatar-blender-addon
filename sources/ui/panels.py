import bpy
from ..properties import *
from ..helpers import get_work_scene, pending_classes
from .. import operators


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


			atlas_setup = self.layout.box()
			atlas_setup.label(text='Texture atlas')
			atlas_setup.operator('frame.auto_assign_atlas')
			atlas_setup.operator('frame.pack_uv_islands')

			bake_targets = self.layout.box()
			bake_targets.label(text='Bake targets')
			bake_targets.operator('frame.validate_targets')

			work_meshes = self.layout.box()
			work_meshes.label(text='Work meshes')
			work_meshes.operator('frame.update_selected_workmesh')
			work_meshes.operator('frame.update_all_workmeshes')

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


			# #TODO - remove or make conditional
			# debug = self.layout.box()
			# debug.label(text='Debug tools')
			# debug.operator('frame.place_holder_for_experiments')




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




class FRAME_PT_batch_bake_targets(frame_panel):
	bl_label = "Bake targets"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):

		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			self.layout.template_list('FRAME_UL_bake_targets', '', HT,  'bake_target_collection', HT, 'selected_bake_target')

			bake_target_actions = self.layout.row(align=True)
			bake_target_actions.operator('frame.add_bake_target')
			bake_target_actions.operator('frame.remove_bake_target')
			bake_target_actions.operator('frame.show_selected_bt')


			#TODO - divy up this into a few functions to make it less messy
			if HT.selected_bake_target != -1:
				et = HT.bake_target_collection[HT.selected_bake_target]
				self.layout.prop_search(et, "object_name", scene, "objects")

				if obj := bpy.data.objects.get(et.object_name):
					if shape_keys := obj.data.shape_keys:
						self.layout.prop_search(et, "shape_key_name", obj.data.shape_keys, "key_blocks")


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
						variants.prop_search(var, 'image', bpy.data, 'images')
						variants.prop_search(var, 'uv_map', obj.data, 'uv_layers')


				self.layout.prop(et, 'uv_mode')

				if et.uv_mode == 'UV_IM_FROZEN':
					self.layout.prop_search(et, 'atlas', bpy.data, 'images')
					if obj:
						#self.layout.prop_search(et, 'uv_map', obj.data, 'uv_layers')
						self.layout.prop(et, 'uv_target_channel')
					else:
						self.layout.label(text=f"UV set: (No object)")
				else:
					self.layout.label(text=f"Atlas: {et.atlas or '(not assigned)'}")
					#self.layout.label(text=f"UV set: {et.uv_map or '(not assigned)'}")
					self.layout.label(text=f"UV target: {et.uv_target_channel}")



			#TODO - add button for synchronizing primary → secondary (where? here or utils?)
			mirrors = self.layout.box()
			mirrors.label(text='Mirrored bake targets')
			mirrors.template_list('FRAME_UL_bake_target_mirrors', '', HT,  'bake_target_mirror_collection', HT, 'selected_bake_target_mirror')

			bake_target_actions = mirrors.row(align=True)
			bake_target_actions.operator('frame.add_bake_target_mirror')
			bake_target_actions.operator('frame.remove_bake_target_mirror')

			if HT.selected_bake_target_mirror != -1:
				tm = HT.bake_target_mirror_collection[HT.selected_bake_target_mirror]
				row = mirrors.row()
				row.operator('frame.set_bake_mirror_primary')
				row.operator('frame.set_bake_mirror_secondary')


			advanced = self.layout.box()
			advanced.label(text='Create from shapekeys')
			advanced.prop_search(HT, 'source_object', scene, 'objects')
			advanced.operator('frame.create_bake_targets_from_shapekeys')