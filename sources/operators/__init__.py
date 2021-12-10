from .base import frame_operator
from . import operations


class FRAME_OT_auto_assign_atlas(frame_operator):
	bl_label = 			"Auto assign atlas/UV"
	bl_idname = 		"frame.auto_assign_atlas"
	bl_description = 	"Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
	frame_operator = 	operations.auto_assign_atlas

class FRAME_OT_update_baking_scene(frame_operator):
	bl_label = 			"Update baking scene"
	bl_idname = 		"frame.update_baking_scene"
	#TODO - bl_description
	frame_operator = 	operations.update_bake_scene

class FRAME_OT_pack_uv_islands(frame_operator):
	bl_label = 			"Pack UV islands"
	bl_idname = 		"frame.pack_uv_islands"
	#TODO - bl_description
	frame_operator = 	operations.pack_uv_islands

class FRAME_OT_bake_all(frame_operator):
	bl_label = 			"Bake all bake targets"
	bl_idname = 		"frame.bake_all"
	#TODO - bl_description
	frame_operator = 	operations.bake_all_bake_targets

class FRAME_OT_bake_selected(frame_operator):
	#TODO - if we support multiple targets in selection we should change to plural here
	bl_label = 			"Bake selected bake target"
	bl_idname = 		"frame.bake_selected"
	#TODO - bl_description
	frame_operator = 	operations.bake_selected_bake_targets

class FRAME_OT_create_bake_targets_from_shapekeys(frame_operator):
	bl_label = 			"Create bake targets"
	bl_description = 	'Creates bake targets based on a specific naming convention'
	bl_idname = 		'frame.create_bake_targets_from_shapekeys'
	frame_operator = 	operations.create_bake_targets_from_shapekeys

class FRAME_OT_set_bake_mirror_primary(frame_operator):
	bl_label = 			"Set primary"
	bl_description = 	'Set primary bake target of selected mirror entry'
	bl_idname = 		'frame.set_bake_mirror_primary'
	frame_operator = 	operations.bake_mirrors.set_primary

class FRAME_OT_set_bake_mirror_secondary(frame_operator):
	bl_label = 			"Set secondary"
	bl_description = 	'Set secondary bake target of selected mirror entry'
	bl_idname = 		'frame.set_bake_mirror_secondary'
	frame_operator = 	operations.bake_mirrors.set_secondary

class FRAME_OT_add_bake_target_mirror(frame_operator):
	bl_label = 			"+"
	bl_description = 	'Create new mirror entry'
	bl_idname = 		'frame.add_bake_target_mirror'
	frame_operator = 	operations.bake_mirrors.add

class FRAME_OT_remove_bake_target_mirror(frame_operator):
	bl_label =			"-"
	bl_description = 	'Remove mirror entry'
	bl_idname = 		'frame.remove_bake_target_mirror'
	frame_operator = 	operations.bake_mirrors.remove

class FRAME_OT_add_bake_target(frame_operator):
	bl_label =			"+"
	bl_description = 	'Create new bake target'
	bl_idname = 		'frame.add_bake_target'
	frame_operator = 	operations.bake_targets.add

class FRAME_OT_remove_bake_target(frame_operator):
	bl_label = 			"-"
	bl_description = 	'Remove selected bake target'
	bl_idname = 		'frame.remove_bake_target'
	frame_operator = 	operations.bake_targets.remove

class FRAME_OT_add_bake_target_variant(frame_operator):
	bl_label = 			"+"
	bl_description = 	'Add variant'
	bl_idname = 		'frame.add_bake_target_variant'
	frame_operator =	operations.bake_variants.add

class FRAME_OT_remove_bake_target_variant(frame_operator):
	bl_label =			"-"
	bl_description = 	'Remove mirror entry'
	bl_idname = 		'frame.remove_bake_target_variant'
	frame_operator = 	operations.bake_variants.remove