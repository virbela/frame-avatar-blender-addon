import bpy
import bmesh
import mathutils
from bpy.types import Context, Operator, Scene

from .common import set_uv_map
from ..utils.logging import log_writer as log
from ..utils.materials import setup_bake_material
from ..utils.properties import HomeomorphicProperties, BakeTarget
from ..utils.constants import PAINTING_UV_MAP, TARGET_UV_MAP, Assets
from ..utils.helpers import (
    create_named_entry,
    require_bake_scene,
    require_work_scene,
    IMPLEMENTATION_PENDING,
    ensure_applied_rotation,
    get_bake_target_variant_name,
)

update_selected_workmesh = IMPLEMENTATION_PENDING
update_selected_workmesh_all_shapekeys = IMPLEMENTATION_PENDING
update_selected_workmesh_active_shapekey = IMPLEMENTATION_PENDING

def create_workmeshes_for_all_targets(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene(context)
    for bake_target in ht.bake_target_collection:
        create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target)


def create_workmeshes_for_selected_target(operator: Operator, context: Context, ht: HomeomorphicProperties):
    if bake_target := ht.get_selected_bake_target():
        bake_scene = require_bake_scene(context)
        create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target)


def update_all_workmeshes(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene(context)
    for bake_target in ht.bake_target_collection:
        for variant in bake_target.variant_collection:
            obj_name = get_bake_target_variant_name(bake_target, variant)
            obj = bake_scene.objects.get(obj_name)
            if obj and not variant.workmesh:
                variant.workmesh = obj
                variant.uv_map = PAINTING_UV_MAP
                bake_target.uv_map = TARGET_UV_MAP

                update_workmesh_materials(bake_target, variant)


def workmesh_to_shapekey(operator: Operator, context: Context, ht: HomeomorphicProperties):
    work_scene = require_work_scene(context)
    avatar_object = work_scene.objects.get('Avatar')
    if not avatar_object:
        return

    for object in  context.selected_objects:
        shape_name = object.name
        # Handle multiple variant names
        if '.' in shape_name:
            shape_name = shape_name.split('.')[0]

        workmesh = object.data
        # -- set corresponding shapekey
        bm = bmesh.new()
        bm.from_mesh(avatar_object.data)
        shape = bm.verts.layers.shape[shape_name]

        for vert in bm.verts:
            vert[shape] = workmesh.vertices[vert.index].co.copy()

        bm.to_mesh(avatar_object.data)
        bm.free()


def all_workmeshes_to_shapekey(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene(context)
    work_scene = require_work_scene(context)
    avatar_object = work_scene.objects.get('Avatar')
    if not avatar_object:
        return

    workmeshes = [m for m in bake_scene.objects if m.type == "MESH"]
    for object in  workmeshes:
        shape_name = object.name
        # Handle multiple variant names
        if '.' in shape_name and 'offset' not in shape_name.lower():
            shape_name = shape_name.split('.')[0]

        workmesh = object.data
        # -- set corresponding shapekey
        bm = bmesh.new()
        bm.from_mesh(avatar_object.data)
        if shape_name not in bm.verts.layers.shape:
            continue

        shape = bm.verts.layers.shape[shape_name]
        for vert in bm.verts:
            vert[shape] = workmesh.vertices[vert.index].co.copy()

        bm.to_mesh(avatar_object.data)
        bm.free()


def shapekey_to_workmesh(operator: Operator, context: Context, ht: HomeomorphicProperties):
    work_scene = require_work_scene(context)
    avatar_object = work_scene.objects.get('Avatar')
    if not avatar_object:
        return

    # -- get mesh data for active shapekey
    shapekey_data = {}
    active_shapekey = avatar_object.data.shape_keys.key_blocks[avatar_object.active_shape_key_index]

    bm = bmesh.new()
    bm.from_mesh(avatar_object.data)
    shape = bm.verts.layers.shape[active_shapekey.name]

    for vert in bm.verts:
        shapekey_data[vert.index] = vert[shape]
    bm.free()

    # -- get corresponding workmesh and update vertices
    bake_scene = require_bake_scene(context)
    workmesh = bake_scene.objects.get(active_shapekey.name)
    if not workmesh:
        print("Missing workmesh!")
        return

    for vert in workmesh.data.vertices:
        vert.co = shapekey_data[vert.index]


def all_shapekeys_to_workmeshes(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene(context)
    work_scene = require_work_scene(context)
    avatar_object = work_scene.objects.get('Avatar')
    if not avatar_object:
        return

    for key in avatar_object.data.shape_keys.key_blocks:
        shapekey_data = {}

        bm = bmesh.new()
        bm.from_mesh(avatar_object.data)
        shape = bm.verts.layers.shape[key.name]

        for vert in bm.verts:
            shapekey_data[vert.index] = vert[shape]
        bm.free()

        # -- get corresponding workmesh and update vertices
        workmesh = bake_scene.objects.get(key.name)
        if not workmesh:
            # -- try get variants
            objects = [o for o in bake_scene.objects if f"{key.name}." in o.name]
            if objects:
                workmesh = objects
            else:
                log.info(f"Missing workmesh for {key.name}!")
                continue

        if isinstance(workmesh, list):
            for wm in workmesh:
                for vert in wm.data.vertices:
                    vert.co = shapekey_data[vert.index]
        else:
            for vert in workmesh.data.vertices:
                vert.co = shapekey_data[vert.index]


def workmesh_symmetrize(operator: Operator, context: Context, ht: HomeomorphicProperties):
    for obj in context.selected_objects:
        mesh = obj.data
        right_verts = [v for v in mesh.vertices if v.co.x > 0.0]
        left_verts = [v for v in mesh.vertices if v.co.x < 0.0]

        print(len(mesh.vertices), len(right_verts) + len(left_verts))

        size = len(left_verts)
        kd = mathutils.kdtree.KDTree(size)
        for v in left_verts:
            kd.insert(v.co, v.index)
        kd.balance()

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()

        for vert in right_verts:
            vert_mirror = vert.co.copy()
            vert_mirror.x *= -1

            _, index, dist = kd.find(vert_mirror)
            if dist > 0.0:
                bm.verts[index].co = vert_mirror

        bm.to_mesh(mesh)
        bm.free()
        mesh.update()


def create_workmeshes_for_specific_target(context: Context, ht: HomeomorphicProperties, bake_scene: Scene, bake_target: BakeTarget):
    for variant in bake_target.variant_collection:

        pending_name = get_bake_target_variant_name(bake_target, variant)

        # if the workmesh was previously created in the bake scene, skip
        if pending_name in bake_scene.objects:
            # NOTE(ranjian0) since artists may have performed actions on the workmeshs,
            # we choose to skip regeneration.
            log.warning(f'Skipping existing workmesh ...')
            pending_object = bake_scene.objects.get(pending_name)
            bake_uv = pending_object.data.uv_layers[TARGET_UV_MAP]
            local_uv = pending_object.data.uv_layers[PAINTING_UV_MAP]

        else:

            if source_object := bake_target.source_object:
                ensure_applied_rotation(source_object)

                pending_object = source_object.copy()
                pending_object.name = pending_name
                pending_object.data = source_object.data.copy()
                pending_object.data.name = pending_name

                # Create UV map for painting
                bake_uv = pending_object.data.uv_layers[0]	# Assume first UV map is the bake one
                bake_uv.name = TARGET_UV_MAP
                local_uv = pending_object.data.uv_layers.new(name=PAINTING_UV_MAP)
                set_uv_map(pending_object, local_uv.name)

                # check if this target uses a shape key
                if _ := pending_object.data.shape_keys.key_blocks.get(bake_target.shape_key_name):
                    #Remove all shapekeys except the one this object represents
                    for key in pending_object.data.shape_keys.key_blocks:
                        if key.name != bake_target.shape_key_name:
                            pending_object.shape_key_remove(key)

                    #Remove remaining
                    for key in pending_object.data.shape_keys.key_blocks:
                        pending_object.shape_key_remove(key)

            bake_scene.collection.objects.link(pending_object)

        variant.workmesh = pending_object
        variant.uv_map = local_uv.name
        bake_target.uv_map = bake_uv.name
        update_workmesh_materials(bake_target, variant)


def update_workmesh_materials(bake_target, variant):
    load_material_templates()

    #TBD - should we disconnect the material if we fail to create one? 
    # This might be good in order to prevent accidentally getting unintended materials activated
    # TODO(ranjian0) Should mirrored baketarget workmeshes have a material
    if not variant.uv_map:
        variant.workmesh.active_material = None
        log.error(f"No uv found for variant {variant}")
        return

    bake_material_name =f'bake-{get_bake_target_variant_name(bake_target, variant)}'
    bake_material = create_named_entry(bpy.data.materials, bake_material_name)
    bake_material.use_nodes = True	#contribution note 9
    #TBD should we use source_uv_map here or should we consider the workmesh to have an intermediate UV map?
    setup_bake_material(bake_material, variant.intermediate_atlas, bake_target.source_uv_map, variant.image, variant.uv_map)
    variant.workmesh.active_material = bake_material


def load_material_templates():
    asset_mat_names = (
        Assets.Materials.BakeAO.name, 
        Assets.Materials.BakeDiffuse.name, 
        Assets.Materials.BakePreview.name
    )
    
    # -- if we have not already loaded the template materials, load them
    if not all(template_material in bpy.data.materials for template_material in asset_mat_names):
        with bpy.data.libraries.load(str(Assets.Materials.url), link=False) as (data_from, data_to):
            data_to.materials = [name for name in data_from.materials if name in asset_mat_names]
        for mat in data_to.materials:
            if mat:
                mat.use_fake_user = True


def mirror_workmesh_verts(operator: Operator, context: Context, ht: HomeomorphicProperties):
    source_obj = ht.mirror_verts_source
    target_obj = ht.mirror_verts_target

    # TODO(ranjian0)
    # For now we assume the mirror axis is the x axis
    
    source_verts = [v for v in source_obj.data.vertices]
    target_verts = [v for v in target_obj.data.vertices]

    size = len(target_verts)
    kd = mathutils.kdtree.KDTree(size)
    for v in target_verts:
        kd.insert(v.co, v.index)
    kd.balance()

    if context.mode == "EDIT_MESH":
        bm = bmesh.from_edit_mesh(target_obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(target_obj.data)
    bm.verts.ensure_lookup_table()

    for vert in source_verts:
        vert_mirror = vert.co.copy()
        vert_mirror.x *= -1

        _, index, dist = kd.find(vert_mirror)
        if dist < ht.mirror_distance:
            bm.verts[index].co = vert_mirror

    if context.mode == "EDIT_MESH":
        bmesh.update_edit_mesh(target_obj.data)
    else:
        bm.to_mesh(target_obj.data)
    bm.free()
    target_obj.data.update()


def transfer_skin_weights(operator: Operator, context: Context, ht: HomeomorphicProperties):
    pass
