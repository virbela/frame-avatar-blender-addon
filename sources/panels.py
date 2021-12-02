# DEPRECHATED - remove


import bpy
from .ui.elements import *
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




