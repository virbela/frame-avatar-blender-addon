import bpy
from .. import utilities
from ..properties import *

@utilities.register_class
class FRAME_PT_workflow(bpy.types.Panel):
	bl_label = "Workflow"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		scene = context.scene
		HT = context.scene.homeomorphictools

		self.layout.operator('frame.update_baking_scene')


@utilities.register_class
class FRAME_PT_batch_bake_targets(bpy.types.Panel):
	bl_label = "Bake targets"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		scene = context.scene
		HT = context.scene.homeomorphictools
		self.layout.template_list('FRAME_UL_bake_targets', '', HT,  'bake_target_collection', HT, 'selected_bake_target')

		bake_target_actions = self.layout.row(align=True)
		bake_target_actions.operator('frame.add_bake_target')
		bake_target_actions.operator('frame.remove_bake_target')


		if HT.selected_bake_target != -1:
			et = HT.bake_target_collection[HT.selected_bake_target]
			self.layout.prop_search(et, "object_name", scene, "objects")

			if obj := bpy.data.objects.get(et.object_name):
				if shape_keys := obj.data.shape_keys:
					self.layout.prop_search(et, "shape_key_name", obj.data.shape_keys, "key_blocks")


			self.layout.prop(et, 'uv_area_weight')
			self.layout.prop(et, 'variant_count')
			self.layout.prop(et, 'uv_mode')


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