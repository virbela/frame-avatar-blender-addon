import bpy
from . import utilities
from .baking import update_bake_scene, bake_all_bake_targets, bake_selected_bake_targets, pack_uv_islands
from .helpers import get_work_scene

#TODO - add documentation for when hovering above an operator in blender

@utilities.register_class
class FRAME_OT_update_baking_scene(bpy.types.Operator):
	bl_label = "Update baking scene"
	bl_idname = "frame.update_baking_scene"

	def execute(self, context):
		update_bake_scene(context)
		return {'FINISHED'}

@utilities.register_class
class FRAME_OT_pack_uv_islands(bpy.types.Operator):
	bl_label = "Pack UV islands"
	bl_idname = "frame.pack_uv_islands"

	def execute(self, context):
		pack_uv_islands(context)
		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_bake_all(bpy.types.Operator):
	bl_label = "Bake all bake targets"
	bl_idname = "frame.bake_all"

	def execute(self, context):
		bake_all_bake_targets(context)
		return {'FINISHED'}



@utilities.register_class
class FRAME_OT_bake_selected(bpy.types.Operator):
	#TODO - if we support multiple targets in selection we should change to plural here
	bl_label = "Bake selected bake target"
	bl_idname = "frame.bake_selected"

	def execute(self, context):
		bake_selected_bake_targets(context)
		return {'FINISHED'}


