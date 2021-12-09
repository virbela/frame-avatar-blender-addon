import bpy
from .. import utilities
from ..exceptions import BakeException
from ..baking import create_bake_targets_from_shapekeys

#TODO - We need to refactor this, make sure we use the correct scene everywhere
#TODO - We should have an abstract way for dealing with lists of things since we have 3 lists so far (bake targets, bake mirrors, bake variants). There might be more.


@utilities.register_class
class FRAME_OT_create_bake_targets_from_shapekeys(bpy.types.Operator):
	bl_label = "Create bake targets"
	bl_description = 'Creates bake targets based on a specific naming convention'
	bl_idname = 'frame.create_bake_targets_from_shapekeys'

	#TODO - fix
	def execute(self, context):

		HT = context.scene.homeomorphictools


		if source := bpy.data.objects.get(HT.source_object):
			shape_keys = source.data.shape_keys.key_blocks
			create_bake_targets_from_shapekeys(context, HT, shape_keys)

		else:
			raise BakeException.NoObjectChosen(HT.source_object)

		return {'FINISHED'}



@utilities.register_class
class FRAME_OT_set_bake_mirror_primary(bpy.types.Operator):
	bl_label = "Set primary"
	bl_description = 'Set primary bake target of selected mirror entry'
	bl_idname = 'frame.set_bake_mirror_primary'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		et = HT.bake_target_collection[HT.selected_bake_target]
		tm = HT.bake_target_mirror_collection[HT.selected_bake_target_mirror]
		tm.primary = et.identifier

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_set_bake_mirror_secondary(bpy.types.Operator):
	bl_label = "Set secondary"
	bl_description = 'Set secondary bake target of selected mirror entry'
	bl_idname = 'frame.set_bake_mirror_secondary'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		et = HT.bake_target_collection[HT.selected_bake_target]
		tm = HT.bake_target_mirror_collection[HT.selected_bake_target_mirror]
		tm.secondary = et.identifier

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_add_bake_target_mirror(bpy.types.Operator):
	bl_label = "+"
	bl_description = 'Create new mirror entry'
	bl_idname = 'frame.add_bake_target_mirror'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		new = HT.bake_target_mirror_collection.add()


		last_id = len(HT.bake_target_mirror_collection) - 1
		HT.selected_bake_target_mirror = last_id

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_remove_bake_target_mirror(bpy.types.Operator):
	bl_label = "-"
	bl_description = 'Remove mirror entry'
	bl_idname = 'frame.remove_bake_target_mirror'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		HT.bake_target_mirror_collection.remove(HT.selected_bake_target_mirror)

		last_id = len(HT.bake_target_mirror_collection) - 1
		if last_id == -1:
			HT.selected_bake_target_mirror = -1
		else:
			HT.selected_bake_target_mirror = min(HT.selected_bake_target_mirror, last_id)

		return {'FINISHED'}




@utilities.register_class
class FRAME_OT_add_bake_target(bpy.types.Operator):
	bl_label = "+"
	bl_description = 'Create new bake target'
	bl_idname = 'frame.add_bake_target'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		new = HT.bake_target_collection.add()

		last_id = len(HT.bake_target_collection) - 1
		HT.selected_bake_target = last_id

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_remove_bake_target(bpy.types.Operator):
	bl_label = "-"
	bl_description = 'Remove selected bake target'
	bl_idname = 'frame.remove_bake_target'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		HT.bake_target_collection.remove(HT.selected_bake_target)

		last_id = len(HT.bake_target_collection) - 1
		if last_id == -1:
			HT.selected_bake_target = -1
		else:
			HT.selected_bake_target = min(HT.selected_bake_target, last_id)

		return {'FINISHED'}



@utilities.register_class
class FRAME_OT_add_bake_target_variant(bpy.types.Operator):
	bl_label = "+"
	bl_description = 'Add variant'
	bl_idname = 'frame.add_bake_target_variant'

	def execute(self, context):
		#TODO - implement
		HT = context.scene.homeomorphictools

		if HT.selected_bake_target != -1:
			et = HT.bake_target_collection[HT.selected_bake_target]

			new = et.variant_collection.add()

			last_id = len(et.variant_collection) - 1
			et.selected_variant = last_id

		else:
			print('ERROR')




		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_remove_bake_target_variant(bpy.types.Operator):
	bl_label = "-"
	bl_description = 'Remove mirror entry'
	bl_idname = 'frame.remove_bake_target_variant'

	def execute(self, context):

		#TODO implement
		# HT = context.scene.homeomorphictools
		# HT.bake_target_mirror_collection.remove(HT.selected_bake_target_mirror)

		# last_id = len(HT.bake_target_mirror_collection) - 1
		# if last_id == -1:
		# 	HT.selected_bake_target_mirror = -1
		# else:
		# 	HT.selected_bake_target_mirror = min(HT.selected_bake_target_mirror, last_id)

		return {'FINISHED'}
