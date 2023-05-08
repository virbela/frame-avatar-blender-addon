import bpy

from . import operations
from .base import FabaOperator
from .common import (
    poll_avatar_mesh,
    poll_bake_scene,
    poll_work_scene,
    poll_baketargets,
)


# Introduction
class FABA_OT_setup_bake_scene(FabaOperator):
    bl_label =            "Create Bake Scene"
    bl_idname =           "faba.setup_bake_scene"
    bl_description =      "Create bake scene"
    faba_operator =       operations.setup_bake_scene

# Export
class FABA_OT_export(FabaOperator):
    bl_label =            "Export GLTF"
    bl_idname =           "faba.export"
    bl_description =      "Export avatar meshes and metadata"
    faba_operator =       operations.export

class FABA_OT_remove_export_json_path(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove JSON path'
    bl_idname =           'faba.remove_json_path'
    faba_operator =       operations.ExportAnimationJSONPaths.remove_json_path

    index:                bpy.props.IntProperty()

class FABA_OT_add_export_json_path(FabaOperator):
    bl_label =            "+"
    bl_description =      'Add JSON path'
    bl_idname =           'faba.add_json_path'
    faba_operator =       operations.ExportAnimationJSONPaths.add_json_path


# Bake Targets
class FABA_OT_create_targets_from_avatar(FabaOperator):
    bl_label =            "New bake targets from avatar mesh"
    bl_idname =           "faba.create_targets_from_avatar_object"
    bl_description =      "Create shape key targets from avatar mesh"
    faba_operator =       operations.create_targets_from_avatar_object
    faba_poll =           poll_avatar_mesh


# Work Meshes
class FABA_OT_create_workmeshes_for_all_targets(FabaOperator):
    bl_label =            "New work meshes from all bake targets"
    bl_idname =           "faba.create_workmeshes_for_all_targets"
    bl_description =      "Create bake meshes for all bake targets"
    faba_operator =       operations.create_workmeshes_for_all_targets
    faba_poll =           poll_baketargets

class FABA_OT_create_workmeshes_for_selected_target(FabaOperator):
    bl_label =            "New work meshes from selected bake targets"
    bl_idname =           "faba.create_workmeshes_for_selected_target"
    bl_description =      "Create bake meshes for the selected bake targets"
    faba_operator =       operations.create_workmeshes_for_selected_target

class FABA_OT_update_selected_workmesh_all_shapekeys(FabaOperator):
    bl_label =            "Update selected"
    bl_idname =           "faba.update_selected_workmesh_all_shapekeys"
    bl_description =      "Update vertex position data for all workmeshes"
    faba_operator =       operations.update_selected_workmesh_all_shapekeys

class FABA_OT_update_selected_workmesh_active_shapekey(FabaOperator):
    bl_label =            "Update active shapekey"
    bl_idname =           "faba.update_selected_workmesh_active_shapekey"
    bl_description =      "Update vertex position data for the active shape key mesh"
    faba_operator =       operations.update_selected_workmesh_active_shapekey

class FABA_OT_update_selected_workmesh(FabaOperator):
    bl_label =            "Update selected work mesh"
    bl_idname =           "faba.update_selected_workmesh"
    #TODO - bl_description
    faba_operator =       operations.update_selected_workmesh

class FABA_OT_update_all_workmeshes(FabaOperator):
    bl_label =            "Update all work meshes"
    bl_idname =           "faba.update_all_workmeshes"
    bl_description =      "Reset all the bake target workmeshes(uv, materials)"
    faba_operator =       operations.update_all_workmeshes


class FABA_OT_workmesh_to_shapekey(FabaOperator):
    bl_label =            "Selected workmesh to shapekey"
    bl_idname =           "faba.workmesh_to_shapekey"
    bl_description =      "Transfer the selected workmesh(es) geometry to the corresponding shapekey(s)"
    faba_operator =       operations.workmesh_to_shapekey
    faba_poll =           poll_bake_scene


class FABA_OT_all_workmeshes_to_shapekeys(FabaOperator):
    bl_label =            "All workmeshes to shapekeys"
    bl_idname =           "faba.all_workmesh_to_shapekey"
    bl_description =      "Transfer the all workmesh geometry to the corresponding shapekey"
    faba_operator =       operations.all_workmeshes_to_shapekey
    faba_poll =           poll_bake_scene


class FABA_OT_shapekey_to_workmesh(FabaOperator):
    bl_label =            "Active shapekey to workmesh"
    bl_idname =           "faba.shapekey_to_workmesh"
    bl_description =      "Transfer the active shapekey geometry to the corresponding workmesh"
    faba_operator =       operations.shapekey_to_workmesh
    faba_poll=           poll_work_scene


class FABA_OT_all_shapekey_to_workmesh(FabaOperator):
    bl_label =            "All shapekeys to workmeshes"
    bl_idname =           "faba.all_shapekey_to_workmesh"
    bl_description =      "Transfer all shapekey geometry to the corresponding workmesh"
    faba_operator =       operations.all_shapekeys_to_workmeshes
    faba_poll =           poll_work_scene


class FABA_OT_workmesh_symmetrize(FabaOperator):
    bl_label =            "Symmetrize workmesh"
    bl_idname =           "faba.workmesh_symmetrize"
    bl_description =      "Make the workmesh symmetrical along X axis"
    faba_operator =       operations.workmesh_symmetrize


class FABA_OT_mirror_workmesh_verts(FabaOperator):
    bl_label =            "Mirror Vertices"
    bl_idname =           "faba.mirror_workmesh_verts"
    bl_description =      "Mirror vertices from source object to target object"
    faba_operator =       operations.mirror_workmesh_verts


# Texture Atlas
class FABA_OT_auto_assign_atlas(FabaOperator):
    bl_label =            "Auto assign atlas/UV"
    bl_idname =           "faba.auto_assign_atlas"
    bl_description =      "Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
    faba_operator =       operations.auto_assign_atlas

class FABA_OT_pack_uv_islands(FabaOperator):
    bl_label =            "Pack UV islands"
    bl_idname =           "faba.pack_uv_islands"
    bl_description =      "Go through the bake targets and pack workmesh uvs into intermediate atlases"
    faba_operator =       operations.pack_uv_islands


# Work Materials
class FABA_OT_update_selected_material(FabaOperator):
    bl_label =            "Update selected baketarget material"
    bl_idname =           "faba.update_selected_material"
    bl_description =      "Update the work mesh material for the selected bake target"
    faba_operator =       operations.update_selected_material

class FABA_OT_update_all_materials(FabaOperator):
    bl_label =            "Update all baketarget materials"
    bl_idname =           "faba.update_all_materials"
    bl_description =      "Update work mesh materials for all bake targets"
    faba_operator =       operations.update_all_materials

class FABA_OT_switch_to_bake_material(FabaOperator):
    bl_label =            "Show bake/paint material"
    bl_description =      'Switch all bake objects to use the bake material'
    bl_idname =           'faba.switch_to_bake_material'
    faba_operator =       operations.switch_to_bake_material

class FABA_OT_switch_to_preview_material(FabaOperator):
    bl_label =            "Show preview material"
    bl_description =      'Switch all bake objects to use the preview material'
    bl_idname =           'faba.switch_to_preview_material'
    faba_operator =       operations.switch_to_preview_material

class FABA_OT_select_by_atlas(FabaOperator):
    bl_label =            "Select work meshes based on atlas"
    bl_idname =           "faba.select_by_atlas"
    bl_description =      "Select all work meshes in `Match atlas`"
    faba_operator =       operations.select_by_atlas

class FABA_OT_set_selected_workmesh_atlas(FabaOperator):
    bl_label =            "Set work mesh atlas"
    bl_idname =           "faba.set_selected_workmesh_atlas"
    bl_description =      "Set the intermediate atlas for all selected workmeshes to `Match atlas`"
    faba_operator =       operations.set_selected_objects_atlas


# Baking
class FABA_OT_bake_selected_bake_target(FabaOperator):
    bl_label =            "Bake selected target"
    bl_idname =           "faba.bake_selected_bake_target"
    bl_description =      "Bake textures for the selected bake target"
    faba_operator =       operations.bake_selected_bake_target

class FABA_OT_bake_selected_workmeshes(FabaOperator):
    bl_label =            "Bake selected work meshes"
    bl_idname =           "faba.bake_selected_workmeshes"
    bl_description =      "Bake textures for selected work meshes"
    faba_operator =       operations.bake_selected_workmeshes

class FABA_OT_bake_all(FabaOperator):
    bl_label =            "Bake all targets"
    bl_idname =           "faba.bake_all"
    bl_description =      "Bake textures for all targets and their variants"
    faba_operator =       operations.bake_all_bake_targets


# Helpers
class FABA_OT_synchronize_uv_to_vertices(FabaOperator):
    bl_label =            "Select mesh vertices based on UV selection"
    bl_idname =           "faba.synchronize_uv_to_vertices"
    bl_description =      "Sync selection state for mesh and uvs"
    faba_operator =       operations.synchronize_uv_to_vertices

class FABA_OT_select_objects_by_uv(FabaOperator):
    bl_label =            "Select objects based on UV selection"
    bl_idname =           "faba.select_objects_by_uv"
    bl_description =      "Select all objects in the active uv"
    faba_operator =       operations.select_objects_by_uv

class FABA_OT_synchronize_visibility_to_render(FabaOperator):
    bl_label =            "Show to render only"
    bl_idname =           "faba.synchronize_visibility_to_render"
    bl_description =      "Will only make objects that are going to be rendered visible in the viewlayer"
    faba_operator =       operations.synchronize_visibility_to_render

class FABA_OT_make_everything_visible(FabaOperator):
    bl_label =            "Show everything"
    bl_idname =           "faba.make_everything_visible"
    bl_description =      "Will make everything in the baking viewlayer visible"
    faba_operator =       operations.make_everything_visible

class FABA_OT_reset_uv_transforms(FabaOperator):
    bl_label =            "Reset UV transforms"
    bl_idname =           "faba.reset_uv_transforms"
    bl_description =      "Resets UV transform to reflect the source object"
    faba_operator =       operations.reset_uv_transforms

class FABA_OT_recalculate_normals(FabaOperator):
    bl_label =            "Recalculate normals on selected meshes"
    bl_idname =           "faba.recalculate_normals"
    bl_description =      "Recalculates normals to combat artifacts"
    faba_operator =       operations.recalculate_normals

class FABA_OT_update_baking_scene(FabaOperator):
    bl_label =            "Update baking scene"
    bl_idname =           "faba.update_baking_scene"
    bl_description =      "Regenerate bake scene objects from bake targets"
    faba_operator =       operations.update_bake_scene

class FABA_OT_synchronize_mirrors(FabaOperator):
    bl_label =            "Synchronize mirrors"
    bl_description =      'Copy settings from all primary targets to secondary targets in the mirror list'
    bl_idname =           'faba.synchronize_mirrors'
    faba_operator =       operations.synchronize_mirrors

class FABA_OT_copy_uv_layers(FabaOperator):
    bl_label =            "Copy UV Layers"
    bl_description =      'Transfer UV layers from one object to another'
    bl_idname =           'faba.copy_uv_layers'
    faba_operator =       operations.copy_uv_layers


# Bake Targets UI List
class FABA_OT_add_bake_target(FabaOperator):
    bl_label =            "Add Baketarget"
    bl_description =      'Create new bake target'
    bl_idname =           'faba.add_bake_target'
    faba_operator =       operations.bake_targets.add

class FABA_OT_show_selected_bt(FabaOperator):
    bl_label =            "Edit selected"
    bl_description =      (
                            'Edit selected bake target.\n'
                            'Activates shape key as needed'
                        )
    bl_idname =           'faba.show_selected_bt'
    faba_operator =       operations.bake_targets.edit_selected

class FABA_OT_remove_bake_target(FabaOperator):
    bl_label =            "Remove Selected"
    bl_description =      'Remove selected bake target'
    bl_idname =           'faba.remove_bake_target'
    faba_operator =       operations.bake_targets.remove

class FABA_OT_add_bake_target_variant(FabaOperator):
    bl_label =            "+"
    bl_description =      'Add variant'
    bl_idname =           'faba.add_bake_target_variant'
    faba_operator =       operations.bake_variants.add

class FABA_OT_remove_bake_target_variant(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove mirror entry'
    bl_idname =           'faba.remove_bake_target_variant'
    faba_operator =       operations.bake_variants.remove

class FABA_OT_set_bake_mirror_primary(FabaOperator):
    bl_label =            "Set primary"
    bl_description =      'Set primary bake target of selected mirror entry'
    bl_idname =           'faba.set_bake_mirror_primary'
    faba_operator =       operations.bake_mirrors.set_primary

class FABA_OT_set_bake_mirror_secondary(FabaOperator):
    bl_label =            "Set secondary"
    bl_description =      'Set secondary bake target of selected mirror entry'
    bl_idname =           'faba.set_bake_mirror_secondary'
    faba_operator =       operations.bake_mirrors.set_secondary

class FABA_OT_add_bake_target_mirror(FabaOperator):
    bl_label =            "+"
    bl_description =      'Create new mirror entry'
    bl_idname =           'faba.add_bake_target_mirror'
    faba_operator =       operations.bake_mirrors.add

class FABA_OT_remove_bake_target_mirror(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove mirror entry'
    bl_idname =           'faba.remove_bake_target_mirror'
    faba_operator =       operations.bake_mirrors.remove


# Bake Group UI List
class FABA_OT_add_bake_group(FabaOperator):
    bl_label =            "+"
    bl_description =      'Create new bake group'
    bl_idname =           'faba.add_bake_group'
    faba_operator =       operations.bake_groups.add

class FABA_OT_remove_bake_group(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove selected bake group'
    bl_idname =           'faba.remove_bake_group'
    faba_operator =       operations.bake_groups.remove

class FABA_OT_add_bake_group_member(FabaOperator):
    bl_label =            "+"
    bl_description =      'Add selected bake target to bake group'
    bl_idname =           'faba.add_bake_group_member'
    faba_operator =       operations.bake_groups.members.add

class FABA_OT_remove_bake_group_member(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove selected member from bake group'
    bl_idname =           'faba.remove_bake_group_member'
    faba_operator =       operations.bake_groups.members.remove

# Effects

class FABA_OT_remove_effect(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove selected effect'
    bl_idname =           'faba.remove_effect'
    faba_operator =       operations.effects.remove

class FABA_OT_add_effect(FabaOperator):
    bl_label =            "+"
    bl_description =      'Add Effect'
    bl_idname =           'faba.add_effect'
    faba_operator =       operations.effects.add


class FABA_OT_remove_position_effect(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove position effect'
    bl_idname =           'faba.remove_position_effect'
    faba_operator =       operations.effects.remove_position_effect

    index:                bpy.props.IntProperty()

class FABA_OT_add_position_effect(FabaOperator):
    bl_label =            "+"
    bl_description =      'Add position effect'
    bl_idname =           'faba.add_position_effect'
    faba_operator =       operations.effects.add_position_effect


class FABA_OT_remove_color_effect(FabaOperator):
    bl_label =            "-"
    bl_description =      'Remove color effect'
    bl_idname =           'faba.remove_color_effect'
    faba_operator =       operations.effects.remove_color_effect

    index: bpy.props.IntProperty()

class FABA_OT_add_color_effect(FabaOperator):
    bl_label =            "+"
    bl_description =      'Add color effect'
    bl_idname =           'faba.add_color_effect'
    faba_operator =       operations.effects.add_color_effect

# DEVMODE

class FABA_OT_clear_bake_scene(FabaOperator):
    bl_label =            "Remove everything from bake scene"
    bl_idname =           "faba.clear_bake_scene"
    bl_description =      "This is for internal development purposes and should not be seen in distribution"
    faba_operator =       operations.clear_bake_scene

class FABA_OT_clear_bake_targets(FabaOperator):
    bl_label =            "Remove all bake targets"
    bl_idname =           "faba.clear_bake_targets"
    bl_description =      "Remove all the bake targets"
    faba_operator =       operations.clear_bake_targets

class FABA_OT_show_bone_debug(FabaOperator):
    bl_label =            "Show bone animation debug"
    bl_idname =           "faba.debug_bone_animation"
    bl_description =      "This is for internal development purposes and should not be seen in distribution"
    faba_operator =       operations.debug_bone_animation



class FABA_OT_start_debug_server(FabaOperator):
    bl_label =            "Start Debugger"
    bl_idname =           "faba.start_debugger"
    bl_description =      "This is for internal development purposes and should not be seen in distribution"
    faba_operator =       operations.start_debug_server


classes = (
    FABA_OT_setup_bake_scene,
    FABA_OT_export,
    FABA_OT_add_export_json_path,
    FABA_OT_remove_export_json_path,
    FABA_OT_create_targets_from_avatar,
    FABA_OT_create_workmeshes_for_all_targets,
    FABA_OT_create_workmeshes_for_selected_target,
    FABA_OT_update_selected_workmesh_all_shapekeys,
    FABA_OT_update_selected_workmesh_active_shapekey,
    FABA_OT_update_selected_workmesh,
    FABA_OT_update_all_workmeshes,
    FABA_OT_workmesh_to_shapekey,
    FABA_OT_all_workmeshes_to_shapekeys,
    FABA_OT_shapekey_to_workmesh,
    FABA_OT_all_shapekey_to_workmesh,
    FABA_OT_workmesh_symmetrize,
    FABA_OT_auto_assign_atlas,
    FABA_OT_pack_uv_islands,
    FABA_OT_update_selected_material,
    FABA_OT_update_all_materials,
    FABA_OT_switch_to_bake_material,
    FABA_OT_switch_to_preview_material,
    FABA_OT_select_by_atlas,
    FABA_OT_set_selected_workmesh_atlas,
    FABA_OT_bake_selected_bake_target,
    FABA_OT_bake_selected_workmeshes,
    FABA_OT_bake_all,
    FABA_OT_synchronize_uv_to_vertices,
    FABA_OT_select_objects_by_uv,
    FABA_OT_synchronize_visibility_to_render,
    FABA_OT_make_everything_visible,
    FABA_OT_reset_uv_transforms,
    FABA_OT_recalculate_normals,
    FABA_OT_update_baking_scene,
    FABA_OT_synchronize_mirrors,
    FABA_OT_copy_uv_layers,
    FABA_OT_add_bake_target,
    FABA_OT_show_selected_bt,
    FABA_OT_remove_bake_target,
    FABA_OT_add_bake_target_variant,
    FABA_OT_remove_bake_target_variant,
    FABA_OT_set_bake_mirror_primary,
    FABA_OT_set_bake_mirror_secondary,
    FABA_OT_add_bake_target_mirror,
    FABA_OT_remove_bake_target_mirror,
    FABA_OT_add_bake_group,
    FABA_OT_remove_bake_group,
    FABA_OT_add_bake_group_member,
    FABA_OT_remove_bake_group_member,
    FABA_OT_remove_effect,
    FABA_OT_add_effect,
    FABA_OT_remove_position_effect,
    FABA_OT_add_position_effect,
    FABA_OT_remove_color_effect,
    FABA_OT_add_color_effect,
    FABA_OT_clear_bake_scene,
    FABA_OT_clear_bake_targets,
    FABA_OT_show_bone_debug,
    FABA_OT_mirror_workmesh_verts,
    FABA_OT_start_debug_server
)

register_ops, unregister_ops = bpy.utils.register_classes_factory(classes)