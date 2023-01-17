import bpy
from collections import deque

from . import operations
from .base import frame_operator
from ..utils.logging import log_writer as log
from ..utils.helpers import (
    set_rendering,
    set_selection,
    register_class,
    pending_classes,
    require_bake_scene,
    get_homeomorphic_tool_state
)

from .common import (
    poll_bake_scene,
    poll_work_scene,
    poll_baketargets,
    poll_selected_objects
)


# Introduction
class FRAME_OT_setup_bake_scene(frame_operator):
    bl_label = 			"Create Bake Scene"
    bl_idname = 		"frame.setup_bake_scene"
    bl_description = 	"Create bake scene"
    frame_operator = 	operations.setup_bake_scene

# Export
class FRAME_OT_export(frame_operator):
    bl_label = 			"Export GLTF"
    bl_idname = 		"frame.export"
    bl_description = 	"Export avatar meshes and metadata"
    frame_operator = 	operations.export


# Bake Targets
class FRAME_OT_create_targets_from_selection(frame_operator):
    bl_label = 			"New bake targets from selected objects"
    bl_idname = 		"frame.create_targets_from_selection"
    bl_description = 	"Create shape key targets from all selected objects"
    frame_operator = 	operations.create_targets_from_selection
    frame_poll =        poll_selected_objects


# Work Meshes
class FRAME_OT_create_workmeshes_for_all_targets(frame_operator):
    bl_label = 			"New work meshes from all bake targets"
    bl_idname = 		"frame.create_workmeshes_for_all_targets"
    bl_description = 	"Create bake meshes for all bake targets"
    frame_operator = 	operations.create_workmeshes_for_all_targets
    frame_poll =        poll_baketargets

class FRAME_OT_create_workmeshes_for_selected_target(frame_operator):
    bl_label = 			"New work meshes from selected bake targets"
    bl_idname = 		"frame.create_workmeshes_for_selected_target"
    bl_description = 	"Create bake meshes for the selected bake targets"
    frame_operator = 	operations.create_workmeshes_for_selected_target

class FRAME_OT_update_selected_workmesh_all_shapekeys(frame_operator):
    bl_label = 			"Update selected"
    bl_idname = 		"frame.update_selected_workmesh_all_shapekeys"
    bl_description = 	"Update vertex position data for all workmeshes"
    frame_operator = 	operations.update_selected_workmesh_all_shapekeys

class FRAME_OT_update_selected_workmesh_active_shapekey(frame_operator):
    bl_label = 			"Update active shapekey"
    bl_idname = 		"frame.update_selected_workmesh_active_shapekey"
    bl_description = 	"Update vertex position data for the active shape key mesh"
    frame_operator = 	operations.update_selected_workmesh_active_shapekey

class FRAME_OT_update_selected_workmesh(frame_operator):
    bl_label = 			"Update selected work mesh"
    bl_idname = 		"frame.update_selected_workmesh"
    #TODO - bl_description
    frame_operator = 	operations.update_selected_workmesh

class FRAME_OT_update_all_workmeshes(frame_operator):
    bl_label = 			"Update all work meshes"
    bl_idname = 		"frame.update_all_workmeshes"
    bl_description =    "Reset all the bake target workmeshes(uv, materials)"
    frame_operator = 	operations.update_all_workmeshes


class FRAME_OT_workmesh_to_shapekey(frame_operator):
    bl_label = 			"Selected workmesh to shapekey"
    bl_idname = 		"frame.workmesh_to_shapekey"
    bl_description =    "Transfer the selected workmesh(es) geometry to the corresponding shapekey(s)"
    frame_operator = 	operations.workmesh_to_shapekey
    frame_poll =        poll_bake_scene


class FRAME_OT_all_workmeshes_to_shapekeys(frame_operator):
    bl_label = 			"All workmeshes to shapekeys"
    bl_idname = 		"frame.all_workmesh_to_shapekey"
    bl_description =    "Transfer the all workmesh geometry to the corresponding shapekey"
    frame_operator = 	operations.all_workmeshes_to_shapekey
    frame_poll =        poll_bake_scene


class FRAME_OT_shapekey_to_workmesh(frame_operator):
    bl_label = 			"Active shapekey to workmesh"
    bl_idname = 		"frame.shapekey_to_workmesh"
    bl_description =    "Transfer the active shapekey geometry to the corresponding workmesh"
    frame_operator = 	operations.shapekey_to_workmesh
    frame_poll=         poll_work_scene


class FRAME_OT_all_shapekey_to_workmesh(frame_operator):
    bl_label = 			"All shapekeys to workmeshes"
    bl_idname = 		"frame.all_shapekey_to_workmesh"
    bl_description =    "Transfer all shapekey geometry to the corresponding workmesh"
    frame_operator = 	operations.all_shapekeys_to_workmeshes
    frame_poll =        poll_work_scene


class FRAME_OT_workmesh_symmetrize(frame_operator):
    bl_label = 			"Symmetrize workmesh"
    bl_idname = 		"frame.workmesh_symmetrize"
    bl_description =    "Make the workmesh symmetrical along X axis"
    frame_operator = 	operations.workmesh_symmetrize


# Texture Atlas
class FRAME_OT_auto_assign_atlas(frame_operator):
    bl_label = 			"Auto assign atlas/UV"
    bl_idname = 		"frame.auto_assign_atlas"
    bl_description = 	"Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
    frame_operator = 	operations.auto_assign_atlas

class FRAME_OT_pack_uv_islands(frame_operator):
    bl_label = 			"Pack UV islands"
    bl_idname = 		"frame.pack_uv_islands"
    bl_description = 	"Go through the bake targets and pack workmesh uvs into intermediate atlases"
    frame_operator = 	operations.pack_uv_islands


# Work Materials
class FRAME_OT_update_selected_material(frame_operator):
    bl_label = 			"Update selected baketarget material"
    bl_idname = 		"frame.update_selected_material"
    bl_description = 	"Update the work mesh material for the selected bake target"
    frame_operator = 	operations.update_selected_material

class FRAME_OT_update_all_materials(frame_operator):
    bl_label = 			"Update all baketarget materials"
    bl_idname = 		"frame.update_all_materials"
    bl_description = 	"Update work mesh materials for all bake targets"
    frame_operator = 	operations.update_all_materials

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

class FRAME_OT_select_by_atlas(frame_operator):
    bl_label = 			"Select work meshes based on atlas"
    bl_idname = 		"frame.select_by_atlas"
    bl_description = 	"Select all work meshes in `Match atlas`"
    frame_operator = 	operations.select_by_atlas

class FRAME_OT_set_selected_workmesh_atlas(frame_operator):
    bl_label = 			"Set work mesh atlas"
    bl_idname = 		"frame.set_selected_workmesh_atlas"
    bl_description = 	"Set the intermediate atlas for all selected workmeshes to `Match atlas`"
    frame_operator = 	operations.set_selected_objects_atlas


# Baking
class FRAME_OT_bake_selected_bake_target(frame_operator):
    bl_label = 			"Bake selected target"
    bl_idname = 		"frame.bake_selected_bake_target"
    bl_description = 	"Bake textures for the selected bake target"
    frame_operator = 	operations.bake_selected_bake_target

class FRAME_OT_bake_selected_workmeshes(frame_operator):
    bl_label = 			"Bake selected work meshes"
    bl_idname = 		"frame.bake_selected_workmeshes"
    bl_description = 	"Bake textures for selected work meshes"
    frame_operator = 	operations.bake_selected_workmeshes

class FRAME_OT_bake_all(frame_operator):
    bl_label = 			"Bake all targets"
    bl_idname = 		"frame.bake_all"
    bl_description = 	"Bake textures for all targets and their variants"
    frame_operator = 	operations.bake_all_bake_targets


# Helpers
class FRAME_OT_synchronize_uv_to_vertices(frame_operator):
    bl_label = 			"Select mesh vertices based on UV selection"
    bl_idname = 		"frame.synchronize_uv_to_vertices"
    bl_description = 	"Sync selection state for mesh and uvs"
    frame_operator = 	operations.synchronize_uv_to_vertices

class FRAME_OT_select_objects_by_uv(frame_operator):
    bl_label = 			"Select objects based on UV selection"
    bl_idname = 		"frame.select_objects_by_uv"
    bl_description = 	"Select all objects in the active uv"
    frame_operator =	operations.select_objects_by_uv

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

class FRAME_OT_update_baking_scene(frame_operator):
    bl_label = 			"Update baking scene"
    bl_idname = 		"frame.update_baking_scene"
    bl_description = 	"Regenerate bake scene objects from bake targets"
    frame_operator = 	operations.update_bake_scene

class FRAME_OT_synchronize_mirrors(frame_operator):
    bl_label =			"Synchronize mirrors"
    bl_description = 	'Copy settings from all primary targets to secondary targets in the mirror list'
    bl_idname = 		'frame.synchronize_mirrors'
    frame_operator = 	operations.synchronize_mirrors

class FRAME_OT_copy_uv_layers(frame_operator):
    bl_label =			"Copy UV Layers"
    bl_description = 	'Transfer UV layers from one object to another'
    bl_idname = 		'frame.copy_uv_layers'
    frame_operator = 	operations.copy_uv_layers


# Bake Targets UI List
class FRAME_OT_add_bake_target(frame_operator):
    bl_label =			"Add Baketarget"
    bl_description = 	'Create new bake target'
    bl_idname = 		'frame.add_bake_target'
    frame_operator = 	operations.bake_targets.add

class FRAME_OT_show_selected_bt(frame_operator):
    bl_label =			"Edit selected"
    bl_description = 	(
                            'Edit selected bake target.\n'
                            'Activates shape key as needed'
                        )
    bl_idname = 		'frame.show_selected_bt'
    frame_operator = 	operations.bake_targets.edit_selected

class FRAME_OT_remove_bake_target(frame_operator):
    bl_label = 			"Remove Selected"
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


# Bake Group UI List
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

# Effects

class FRAME_OT_remove_effect(frame_operator):
    bl_label = 			"-"
    bl_description = 	'Remove selected effect'
    bl_idname = 		'frame.remove_effect'
    frame_operator = 	operations.effects.remove

class FRAME_OT_add_effect(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Add Effect'
    bl_idname = 		'frame.add_effect'
    frame_operator =	operations.effects.add


class FRAME_OT_remove_position_effect(frame_operator):
    bl_label = 			"-"
    bl_description = 	'Remove position effect'
    bl_idname = 		'frame.remove_position_effect'
    frame_operator = 	operations.effects.remove_position_effect

    index: bpy.props.IntProperty()

class FRAME_OT_add_position_effect(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Add position effect'
    bl_idname = 		'frame.add_position_effect'
    frame_operator =	operations.effects.add_position_effect


class FRAME_OT_remove_color_effect(frame_operator):
    bl_label = 			"-"
    bl_description = 	'Remove color effect'
    bl_idname = 		'frame.remove_color_effect'
    frame_operator = 	operations.effects.remove_color_effect

    index: bpy.props.IntProperty()

class FRAME_OT_add_color_effect(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Add color effect'
    bl_idname = 		'frame.add_color_effect'
    frame_operator =	operations.effects.add_color_effect

# DEVMODE
class FRAME_OT_node_get_links(frame_operator):
    bl_label = 			"Copy links"
    bl_idname = 		"frame.create_node_script"
    bl_description =	"Enumerate links to stdout for programmtic replication"
    frame_operator = 	operations.devtools.get_node_links

class FRAME_OT_clear_bake_scene(frame_operator):
    bl_label = 			"Remove everything from bake scene"
    bl_idname = 		"frame.clear_bake_scene"
    bl_description =	"This is for internal development purposes and should not be seen in distribution"
    frame_operator = 	operations.clear_bake_scene

class FRAME_OT_clear_bake_targets(frame_operator):
    bl_label = 			"Remove all bake targets"
    bl_idname = 		"frame.clear_bake_targets"
    bl_description =	"Remove all the bake targets"
    frame_operator =	operations.clear_bake_targets
