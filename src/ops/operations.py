from .ops_intro import setup_bake_scene
from .ops_export import export, ExportAnimationJSONPaths

from .ops_baketargets import (
    effects,
    bake_groups,
    bake_targets,
    bake_mirrors,
    bake_variants,
    create_targets_from_avatar_object
)

from .ops_baking import (
    bake_all_bake_targets,
    bake_selected_workmeshes,
    bake_selected_bake_target
)

from .ops_dev import (
    clear_bake_scene,
    start_debug_server,
    clear_bake_targets,
    debug_bone_animation,
)

from .ops_helpers import (
    copy_uv_layers,
    update_bake_scene,
    reset_uv_transforms,
    recalculate_normals,
    synchronize_mirrors,
    select_objects_by_uv,
    make_everything_visible,
    synchronize_uv_to_vertices,
    synchronize_visibility_to_render
)

from .ops_texture import  (
    pack_uv_islands,
    auto_assign_atlas
)

from .ops_workmaterial import (
    select_by_atlas,
    update_all_materials,
    switch_to_bake_material,
    update_selected_material,
    set_selected_objects_atlas,
    switch_to_preview_material
)

from .ops_workmesh import (
    workmesh_symmetrize,
    workmesh_to_shapekey,
    shapekey_to_workmesh,
    update_all_workmeshes,
    mirror_workmesh_verts,
    update_selected_workmesh,
    all_workmeshes_to_shapekey,
    all_shapekeys_to_workmeshes,
    create_workmeshes_for_all_targets,
    create_workmeshes_for_selected_target,
    update_selected_workmesh_all_shapekeys,
    update_selected_workmesh_active_shapekey
)
