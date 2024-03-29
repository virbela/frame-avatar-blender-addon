import bpy
from bpy.types import Operator, Context, ShapeKey, Object

from .common import generic_list
from ..utils.constants import TARGET_UV_MAP
from ..utils.logging import log_writer as log
from ..utils.structures import intermediate, iter_dc
from ..utils.properties import HomeomorphicProperties, BakeTargetMirrorEntry
from ..utils.helpers import a_get, a_set, popup_message, require_work_scene, set_scene, set_selection


def create_targets_from_avatar_object(operator: Operator, context: Context, ht: HomeomorphicProperties):
    source_object = ht.avatar_mesh
    source_uv = source_object.data.uv_layers[0]	# Assume first UV map is the source one
    source_uv.name = TARGET_UV_MAP

    if shape_keys := source_object.data.shape_keys:
        create_baketarget_from_key_blocks(ht, source_object, shape_keys.key_blocks)
    else:
        popup_message("Avatar mesh has no shape keys!", "Mesh Error")
        return

    for mirror in ht.bake_target_mirror_collection:
        bk = ht.bake_target_collection[mirror.secondary]
        bk.bake_mode = 'UV_BM_MIRRORED'


def create_baketarget_from_key_blocks(ht: HomeomorphicProperties, source_object: Object, key_blocks: list[ShapeKey]):
    #Create all intermediate targets
    targets = dict()
    mirror_list = list()

    for sk in key_blocks:
        key = sk.name
        targets[key] = intermediate.pending.bake_target(
            name = f'{source_object.name}_{key}',
            object_name = source_object.name,
            source_object = source_object,
            bake_target = source_object,
            shape_key_name = key,
            uv_mode = 'UV_IM_MONOCHROME',
        )

    #Configure targets and mirrors
    for key, target in targets.items():
        if key.endswith('_L'):
            base = key[:-2]
            Rk = f'{base}_R'
            R = targets.get(Rk)

            if R:
                mirror_list.append(intermediate.mirror(target, R))
            else:
                log.error(f"Could not create mirror for {key} since there was no such object `{Rk}`")

        elif key.endswith('_R'):
            pass

        elif key.endswith('__None'):
            target.uv_mode = 'UV_IM_NIL'

    #Create bake targets
    for target in targets.values():
        if 'basis' in  target.name.lower():
            continue

        if target.name in [bt.name for bt in ht.bake_target_collection]:
            log.info("Skip existing bake target")
            continue


        new = ht.bake_target_collection.add()
        new.variant_collection.add()	# add default variant
        for key, value in iter_dc(target):
            setattr(new, key, value)

        target.bake_target = new

    def create_mirror(primary: int, secondary: int) -> BakeTargetMirrorEntry:
        new = ht.bake_target_mirror_collection.add()
        new.primary = primary
        new.secondary = secondary
        return new

    for mirror in mirror_list:
        create_mirror(ht.get_bake_target_index(mirror.primary.bake_target), ht.get_bake_target_index(mirror.secondary.bake_target))

class bake_mirrors:
    def set_primary(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if mirror := ht.get_selected_mirror():
            if bake_target := ht.get_selected_bake_target():
                mirror.primary = ht.get_bake_target_index(bake_target)

    def set_secondary(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if mirror := ht.get_selected_mirror():
            if bake_target := ht.get_selected_bake_target():
                mirror.secondary = ht.get_bake_target_index(bake_target)

    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.add(ht.bake_target_mirror_collection, a_get(ht, 'selected_bake_target_mirror'), a_set(ht, 'selected_bake_target_mirror'))

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.remove(ht.bake_target_mirror_collection, a_get(ht, 'selected_bake_target_mirror'), a_set(ht, 'selected_bake_target_mirror'))


class bake_targets:
    #BUG - currently we don't check if a target is in a mirror and therefore a mirror will point to the wrong thing if removing a reference

    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.add(ht.bake_target_collection, a_get(ht, 'selected_bake_target'), a_set(ht, 'selected_bake_target'))

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.remove(ht.bake_target_collection, a_get(ht, 'selected_bake_target'), a_set(ht, 'selected_bake_target'))

    #TDB use?
    def edit_selected(operator: Operator, context: Context, ht: HomeomorphicProperties):
        bake_target = ht.get_selected_bake_target()
        if not bake_target:
            return

        bto = bake_target.get_object()
        if not bto:
            return

        work_scene = require_work_scene(context)
        set_scene(context, work_scene)
        view_layer = context.view_layer
        set_selection(view_layer.objects, bto)
        if bake_target.shape_key_name:
            bto.active_shape_key_index = bto.data.shape_keys.key_blocks.find(bake_target.shape_key_name) #tech-note 4

        bpy.ops.object.mode_set(mode='EDIT')


class bake_groups:

    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.add(ht.bake_group_collection, a_get(ht, 'selected_bake_group'), a_set(ht, 'selected_bake_group'))

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.remove(ht.bake_group_collection, a_get(ht, 'selected_bake_group'), a_set(ht, 'selected_bake_group'))


    class members:
        def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
            if bake_group := ht.get_selected_bake_group():
                if bake_target := ht.get_selected_bake_target():
                    new = generic_list.add(bake_group.members, a_get(bake_group, 'selected_member'), a_set(bake_group, 'selected_member'))
                    new.target = ht.get_bake_target_index(bake_target)

        def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
            if bake_group := ht.get_selected_bake_group():
                generic_list.remove(bake_group.members, a_get(bake_group, 'selected_member'), a_set(bake_group, 'selected_member'))


class bake_variants:

    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if bake_target := ht.get_selected_bake_target():
            generic_list.add(bake_target.variant_collection, a_get(bake_target, 'selected_variant'), a_set(bake_target, 'selected_variant'))

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if bake_target := ht.get_selected_bake_target():
            generic_list.remove(bake_target.variant_collection, a_get(bake_target, 'selected_variant'), a_set(bake_target, 'selected_variant'))


class effects:

    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.add(ht.effect_collection, a_get(ht, 'selected_effect'), a_set(ht, 'selected_effect'))

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        generic_list.remove(ht.effect_collection, a_get(ht, 'selected_effect'), a_set(ht, 'selected_effect'))

    def add_position_effect(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            pos = et.positions.add()

    def remove_position_effect(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            et.positions.remove(operator.index)

    def add_color_effect(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            pos = et.colors.add()

    def remove_color_effect(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            et.colors.remove(operator.index)
