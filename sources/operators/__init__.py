from . import operations
from .base import frame_operator


class FRAME_OT_select_by_atlas(frame_operator):
	bl_label = 			"Select work meshes based on atlas"
	bl_idname = 		"frame.select_by_atlas"
	#TODO - bl_description
	frame_operator = 	operations.select_by_atlas

class FRAME_OT_synchronize_uv_to_vertices(frame_operator):
	bl_label = 			"Select mesh vertices based on UV selection"
	bl_idname = 		"frame.synchronize_uv_to_vertices"
	#TODO - bl_description
	frame_operator = 	operations.synchronize_uv_to_vertices

class FRAME_OT_create_workmeshes_for_all_targets(frame_operator):
	bl_label = 			"New work meshes from all bake targets"
	bl_idname = 		"frame.create_workmeshes_for_all_targets"
	#TODO - bl_description
	frame_operator = 	operations.create_workmeshes_for_all_targets

class FRAME_OT_create_workmeshes_for_selected_target(frame_operator):
	bl_label = 			"New work meshes from selected bake targets"
	bl_idname = 		"frame.create_workmeshes_for_selected_target"
	#TODO - bl_description
	frame_operator = 	operations.create_workmeshes_for_selected_target

class FRAME_OT_create_targets_from_selection(frame_operator):
	bl_label = 			"New bake targets from selected objects"
	bl_idname = 		"frame.create_targets_from_selection"
	#TODO - bl_description
	frame_operator = 	operations.create_targets_from_selection

class FRAME_OT_update_selected_workmesh_all_shapekeys(frame_operator):
	bl_label = 			"Update selected"
	bl_idname = 		"frame.update_selected_workmesh_all_shapekeys"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_workmesh_all_shapekeys

class FRAME_OT_update_selected_workmesh_active_shapekey(frame_operator):
	bl_label = 			"Update active shapekey"
	bl_idname = 		"frame.update_selected_workmesh_active_shapekey"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_workmesh_active_shapekey

class FRAME_OT_setup_bake_scene(frame_operator):
	bl_label = 			"First time setup"
	bl_idname = 		"frame.setup_bake_scene"
	bl_description = 	"Create bake scene"
	frame_operator = 	operations.setup_bake_scene

class FRAME_OT_validate_targets(frame_operator):
	bl_label = 			"Validate bake targets"
	bl_idname = 		"frame.validate_targets"
	#TODO - bl_description
	frame_operator = 	operations.validate_targets

class FRAME_OT_update_selected_workmesh(frame_operator):
	bl_label = 			"Update selected work mesh"
	bl_idname = 		"frame.update_selected_workmesh"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_workmesh

class FRAME_OT_update_all_workmeshes(frame_operator):
	bl_label = 			"Update all work meshes"
	bl_idname = 		"frame.update_all_workmeshes"
	#TODO - bl_description
	frame_operator = 	operations.update_all_workmeshes

class FRAME_OT_update_selected_material(frame_operator):
	bl_label = 			"Update selected material"
	bl_idname = 		"frame.update_selected_material"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_material

class FRAME_OT_update_all_materials(frame_operator):
	bl_label = 			"Update all materials"
	bl_idname = 		"frame.update_all_materials"
	#TODO - bl_description
	frame_operator = 	operations.update_all_materials

class FRAME_OT_auto_assign_atlas(frame_operator):
	bl_label = 			"Auto assign atlas/UV"
	bl_idname = 		"frame.auto_assign_atlas"
	bl_description = 	"Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
	frame_operator = 	operations.auto_assign_atlas

#TBD - should we have this one?
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

class FRAME_OT_bake_selected_bake_target(frame_operator):
	#TODO - if we support multiple targets in selection we should change to plural here
	bl_label = 			"Bake selected bake target"
	bl_idname = 		"frame.bake_selected_bake_target"
	#TODO - bl_description
	frame_operator = 	operations.bake_selected_bake_target

class FRAME_OT_bake_selected_workmeshes(frame_operator):
	#TODO - if we support multiple targets in selection we should change to plural here
	bl_label = 			"Bake selected work meshes"
	bl_idname = 		"frame.bake_selected_workmeshes"
	#TODO - bl_description
	frame_operator = 	operations.bake_selected_workmeshes

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

class FRAME_OT_add_bake_group(frame_operator):
	bl_label = 			"+"
	bl_description = 	'Create new bake group'
	bl_idname = 		'frame.add_bake_group'
	frame_operator = 	operations.bake_groups.add

class FRAME_OT_remove_bake_group(frame_operator):
	bl_label =			"-"
	bl_description = 	'Remove selected bake group'
	bl_idname = 		'frame.remove_bake_group'
	frame_operator = 	operations.bake_groups.remove

class FRAME_OT_add_bake_group_member(frame_operator):
	bl_label = 			"+"
	bl_description = 	'Add selected bake target to bake group'
	bl_idname = 		'frame.add_bake_group_member'
	frame_operator = 	operations.bake_groups.members.add

class FRAME_OT_remove_bake_group_member(frame_operator):
	bl_label =			"-"
	bl_description = 	'Remove selected member from bake group'
	bl_idname = 		'frame.remove_bake_group_member'
	frame_operator = 	operations.bake_groups.members.remove

class FRAME_OT_add_bake_target(frame_operator):
	bl_label =			"+"
	bl_description = 	'Create new bake target'
	bl_idname = 		'frame.add_bake_target'
	frame_operator = 	operations.bake_targets.add

class FRAME_OT_show_selected_bt(frame_operator):
	bl_label =			"Edit selected"
	bl_description = 	(
							'Edit selected bake target.\n'
							'Activates shape key is needed'
						)
	bl_idname = 		'frame.show_selected_bt'
	frame_operator = 	operations.bake_targets.edit_selected

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

class FRAME_OT_switch_to_bake_material(frame_operator):
	bl_label =			"Show bake/paint material"
	bl_description = 	'Switch all bake objects to use the bake material'
	bl_idname = 		'frame.switch_to_bake_material'
	frame_operator = 	operations.switch_to_bake_material

class FRAME_OT_switch_to_preview_material(frame_operator):
	bl_label =			"Show preview material"
	bl_description = 	'Switch all bake objects to use the preview material'
	bl_idname = 		'frame.switch_to_preview_material'
	frame_operator = 	operations.switch_to_preview_material

class FRAME_OT_synchronize_mirrors(frame_operator):
	bl_label =			"Synchronize mirrors"
	bl_description = 	'Copy settings from all primary targets to secondary targets in the mirror list'
	bl_idname = 		'frame.synchronize_mirrors'
	frame_operator = 	operations.synchronize_mirrors


#TODO - this should be guarded by a devmode boolean
class FRAME_OT_node_get_links(frame_operator):
	bl_label = 			"Copy links"
	bl_idname = 		"frame.create_node_script"
	bl_description =	"Enumerate links to stdout for programmtic replication"
	frame_operator = 	operations.devtools.get_node_links

#TODO - this should be guarded by a devmode boolean
class FRAME_OT_clear_bake_scene(frame_operator):
	bl_label = 			"Remove everything from bake scene"
	bl_idname = 		"frame.clear_bake_scene"
	bl_description =	"This is for internal development purposes and should not be seen in distribution"
	frame_operator = 	operations.clear_bake_scene

#TODO - this should be guarded by a devmode boolean
class FRAME_OT_clear_bake_targets(frame_operator):
	bl_label = 			"Remove all bake targets"
	bl_idname = 		"frame.clear_bake_targets"
	bl_description =	"This is for internal development purposes and should not be seen in distribution"
	frame_operator =	operations.clear_bake_targets

class FRAME_OT_select_objects_by_uv(frame_operator):
	bl_label = 			"Select objects based on UV selection"
	bl_idname = 		"frame.select_objects_by_uv"
	#TODO bl_description
	frame_operator =	operations.select_objects_by_uv

class FRAME_OT_reset_uv_transforms(frame_operator):
	bl_label = 			"Reset UV transforms"
	bl_idname = 		"frame.reset_uv_transforms"
	bl_description =	"Resets UV transform to reflect the source object"
	frame_operator = 	operations.reset_uv_transforms

class FRAME_OT_recalculate_normals(frame_operator):
	bl_label = 			"Recalculate normals on selected meshes"
	bl_idname = 		"frame.recalculate_normals"
	bl_description =	"Recalculates normals to combat artifacts"
	frame_operator = 	operations.recalculate_normals

class FRAME_OT_synchronize_visibility_to_render(frame_operator):
	bl_label = 			"Show to render only"
	bl_idname = 		"frame.synchronize_visibility_to_render"
	bl_description =	"Will only make objects that are going to be rendered visible in the viewlayer"
	frame_operator = 	operations.synchronize_visibility_to_render

class FRAME_OT_make_everything_visible(frame_operator):
	bl_label = 			"Show everything"
	bl_idname = 		"frame.make_everything_visible"
	bl_description =	"Will make everything in the baking viewlayer visible"
	frame_operator = 	operations.make_everything_visible
