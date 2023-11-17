import bpy

from .ops_intro import FABA_OT_setup_bake_scene
from .ops_animation import FABA_OT_transfer_skin_weights

from .ops_baking import (
    FABA_OT_bake_all,
    FABA_OT_bake_selected_bake_target,
    FABA_OT_bake_selected_workmeshes,
)

from .ops_dev import (
    FABA_OT_clear_bake_scene,
    FABA_OT_clear_bake_targets,
    FABA_OT_show_bone_debug,
    FABA_OT_start_debug_server,
    FABA_OT_custom_debug_operator,
)

from .ops_effects import (
    FABA_OT_add_color_effect,
    FABA_OT_add_effect,
    FABA_OT_add_position_effect,
    FABA_OT_remove_color_effect,
    FABA_OT_remove_effect,
    FABA_OT_remove_position_effect,
)

from .ops_export import (
    FABA_OT_add_export_json_path,
    FABA_OT_export,
    FABA_OT_remove_export_json_path,
)

from .ops_helpers import (
    FABA_OT_copy_uv_layers,
    FABA_OT_make_everything_visible,
    FABA_OT_recalculate_normals,
    FABA_OT_reset_uv_transforms,
    FABA_OT_select_objects_by_uv,
    FABA_OT_synchronize_uv_to_vertices,
    FABA_OT_synchronize_visibility_to_render,
    FABA_OT_update_baking_scene,
)

from .ops_texture import (
    FABA_OT_auto_assign_atlas,
    FABA_OT_pack_uv_islands,
)

from .ops_workmaterial import (
    FABA_OT_select_by_atlas,
    FABA_OT_set_selected_workmesh_atlas,
    FABA_OT_switch_to_bake_material,
    FABA_OT_switch_to_preview_material,
    FABA_OT_update_all_materials,
    FABA_OT_update_selected_material,
)

from .ops_workmesh import (
    FABA_OT_all_shapekey_to_workmesh,
    FABA_OT_all_workmeshes_to_shapekeys,
    FABA_OT_create_workmeshes_for_all_targets,
    FABA_OT_create_workmeshes_for_selected_target,
    FABA_OT_mirror_workmesh_verts,
    FABA_OT_shapekey_to_workmesh,
    FABA_OT_update_all_workmeshes,
    FABA_OT_update_selected_workmesh_active_shapekey,
    FABA_OT_update_selected_workmesh_all_shapekeys,
    FABA_OT_update_selected_workmesh,
    FABA_OT_workmesh_symmetrize,
    FABA_OT_workmesh_to_shapekey,
)


classes = (
    FABA_OT_setup_bake_scene,
    FABA_OT_export,
    FABA_OT_transfer_skin_weights,
    FABA_OT_add_export_json_path,
    FABA_OT_remove_export_json_path,
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
    FABA_OT_copy_uv_layers,
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
    FABA_OT_start_debug_server,
    FABA_OT_custom_debug_operator
)

register_ops, unregister_ops = bpy.utils.register_classes_factory(classes)