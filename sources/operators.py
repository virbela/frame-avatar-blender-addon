import bpy
from . import utilities
from .baking import update_bake_scene
from . import logging


@utilities.register_class
class FRAME_OT_update_baking_scene(bpy.types.Operator):
	bl_label = "Update baking scene"
	bl_idname = "frame.update_baking_scene"

	def execute(self, context):

		HT = context.scene.homeomorphictools

		with logging.log(context) as log:
			log.debug('Debug info')

		update_bake_scene(context)

		return {'FINISHED'}


