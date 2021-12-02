import bpy
from .ui_elements import *
from . import utilities

# #UI panels
# #@utilities.register_class
# class BAKETARGET_PT_main_panel(bpy.types.Panel):
# 	bl_label = "Create bake targets"
# 	bl_idname = "BAKETARGETS_PT_main_panel"
# 	bl_space_type = 'VIEW_3D'
# 	bl_region_type = 'UI'
# 	bl_category = "Avatar"

# 	def draw(self, context):
# 		layout = self.layout
# 		scene = context.scene

# 		layout.prop_search(scene.homeomorphictools, "avatar_string", scene, "objects")
# 		layout.operator("targetcreate.mainoperator")

# #@utilities.register_class
# class PACK_PT_main_panel(bpy.types.Panel):
# 	bl_label = "Packing"
# 	bl_idname = "PACKING_PT_main_panel"
# 	bl_space_type = 'VIEW_3D'
# 	bl_region_type = 'UI'
# 	bl_category = "Avatar"

# 	def draw(self, context):
# 		layout = self.layout
# 		scene = context.scene
# 		homeomorphictools = scene.homeomorphictools

# 		layout.prop(homeomorphictools, "imgsize_int")
# 		layout.prop(homeomorphictools, "uvset_string")
# 		layout.prop(homeomorphictools, "relative_bool")
# 		layout.prop(homeomorphictools, "packer_bool")
# 		layout.operator("pack.mainoperator")

# #@utilities.register_class
# class BATCHBAKE_PT_main_panel(bpy.types.Panel):
# 	bl_label = "Batch bake"
# 	bl_idname = "BATCHBAKING_PT_main_panel"
# 	bl_space_type = 'VIEW_3D'
# 	bl_region_type = 'UI'
# 	bl_category = "Avatar"

# 	def draw(self, context):
# 		layout = self.layout
# 		scene = context.scene
# 		homeomorphictools = scene.homeomorphictools

# 		layout.prop(homeomorphictools, "ao_bool")
# 		layout.prop(homeomorphictools, "persistent_bool")
# 		layout.operator("batch.mainoperator")


# #@utilities.register_class
# class EXPORTGLTF_PT_main_panel(bpy.types.Panel):
# 	bl_label = "Export glTF"
# 	bl_idname = "EXPORTGLTFS_PT_main_panel"
# 	bl_space_type = 'VIEW_3D'
# 	bl_region_type = 'UI'
# 	bl_category = "Avatar"

# 	def draw(self, context):
# 		self.layout.operator("exportgltf.mainoperator")




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
