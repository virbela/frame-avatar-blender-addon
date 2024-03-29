import bpy
from bpy.types import Context, Operator

from ..utils.constants import MIRROR_TYPE
from ..utils.logging import log_writer as log
from ..utils.materials import setup_bake_material, get_material_variants
from ..utils.properties import HomeomorphicProperties, BakeTarget, BakeVariant
from ..utils.helpers import (
    set_scene,
    set_selection,
    require_bake_scene,
    require_named_entry,
    get_bake_target_variant_name
)

def update_all_materials(operator: Operator, context: Context, ht: HomeomorphicProperties):
    for bake_target in ht.bake_target_collection:
        for _, variant in bake_target.iter_variants():
            update_workmesh_materials(context, ht, bake_target, variant)


def update_selected_material(operator: Operator, context: Context, ht: HomeomorphicProperties):
    if bake_target := ht.get_selected_bake_target():
        if variant := bake_target.variant_collection[bake_target.selected_variant]:
            update_workmesh_materials(context, ht, bake_target, variant)


def set_selected_objects_atlas(operator: Operator, context: Context, ht: HomeomorphicProperties):
    selected_objects = context.selected_objects
    for bake_target in ht.bake_target_collection:
        for _, variant in bake_target.iter_variants():
            if variant.workmesh in selected_objects:
                variant.intermediate_atlas = ht.select_by_atlas_image
                update_workmesh_materials(context, ht, bake_target, variant)


def switch_to_bake_material(operator: Operator, context: Context, ht: HomeomorphicProperties):
    generic_switch_to_material(context, ht, 'bake')


def switch_to_preview_material(operator: Operator, context: Context, ht: HomeomorphicProperties):
    generic_switch_to_material(context, ht, 'preview')


def select_by_atlas(operator: Operator, context: Context, ht: HomeomorphicProperties):
    selection = list()
    for bake_target in ht.bake_target_collection:
        for _, variant in bake_target.iter_variants():
            if variant.intermediate_atlas == ht.select_by_atlas_image:
                selection.append(variant.workmesh)


    bake_scene = require_bake_scene(context)
    view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
    set_scene(context, bake_scene)
    set_selection(view_layer.objects, *selection, synchronize_active=True, make_sure_active=True)


def update_workmesh_materials(context: Context, ht: HomeomorphicProperties,  bake_target: BakeTarget, variant: BakeVariant):
    #TODO Handle mirror bake targets properly i.e this fails when no uv map is found
    #TBD - should we disconnect the material if we fail to create one? This might be good in order to prevent accidentally getting unintended materials activated
    if not variant.uv_map:
        variant.workmesh.active_material = None
        log.error(f'Missing UV map for {variant}')
        return

    bake_material_name =f'bake-{get_bake_target_variant_name(bake_target, variant)}'
    if bake_material_name in bpy.data.materials:
        # Remove existing
        bpy.data.materials.remove(bpy.data.materials[bake_material_name])

    bake_material = bpy.data.materials.new(bake_material_name)
    bake_material.use_nodes = True	#contribution note 9
    #TBD should we use source_uv_map here or should we consider the workmesh to have an intermediate UV map?
    setup_bake_material(bake_material, variant.intermediate_atlas, bake_target.source_uv_map, variant.image, variant.uv_map)
    variant.workmesh.active_material = bake_material


def generic_switch_to_material(context: Context, ht: HomeomorphicProperties, material_type: str):
    bake_scene = require_bake_scene(context)
    #todo note 1
    for bt in ht.bake_target_collection:
        _, mt = bt.get_mirror_type(ht)
        if mt is MIRROR_TYPE.SECONDARY:
            continue

        atlas = bt.atlas
        uv_map = bt.source_uv_map

        if atlas and uv_map:
            variant_materials = get_material_variants(bt, bake_scene, atlas, uv_map)

            for variant_name, _ in bt.iter_bake_scene_variants():
                target = require_named_entry(bake_scene.objects, variant_name)
                materials = variant_materials[variant_name]
                target.active_material = bpy.data.materials[getattr(materials, material_type)]
        else:
            log.warning(f'{bt.name} lacks atlas or uv_map')
