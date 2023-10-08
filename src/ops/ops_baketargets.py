import bpy
from bpy.types import Operator, Context, ShapeKey, Object

from .base import FabaOperator
from .common import GenericList, poll_avatar_mesh

from ..utils.constants import TARGET_UV_MAP
from ..utils.logging import log
from ..utils.structures import Intermediate, iter_dc
from ..props import HomeomorphicProperties, BakeTargetMirrorEntry
from ..utils.helpers import (
    AttrGet,
    AttrSet,
    popup_message,
    require_work_scene,
    set_scene,
    set_selection,
)


def create_targets_from_avatar_object(
    operator: Operator, context: Context, ht: HomeomorphicProperties
):
    source_object = ht.avatar_mesh
    source_uv = source_object.data.uv_layers[0]  # Assume first UV map is the source one
    source_uv.name = TARGET_UV_MAP

    if shape_keys := source_object.data.shape_keys:
        create_baketarget_from_key_blocks(ht, source_object, shape_keys.key_blocks)
    else:
        popup_message("Avatar mesh has no shape keys!", "Mesh Error")
        return

    for mirror in ht.bake_target_mirror_collection:
        bk = ht.bake_target_collection[mirror.secondary]
        bk.bake_mode = "UV_BM_MIRRORED"


def create_baketarget_from_key_blocks(
    ht: HomeomorphicProperties, source_object: Object, key_blocks: list[ShapeKey]
):
    # Create all intermediate targets
    targets = dict()
    mirror_list = list()

    for sk in key_blocks:
        key = sk.name
        targets[key] = Intermediate.Pending.BakeTarget(
            name=f"{source_object.name}_{key}",
            object_name=source_object.name,
            source_object=source_object,
            bake_target=source_object,
            shape_key_name=key,
            uv_mode="UV_IM_MONOCHROME",
        )

    # Configure targets and mirrors
    for key, target in targets.items():
        if key.endswith("_L"):
            base = key[:-2]
            Rk = f"{base}_R"
            R = targets.get(Rk)

            if R:
                mirror_list.append(Intermediate.Mirror(target, R))
            else:
                log.error(
                    f"Could not create mirror for {key} since there was no such object `{Rk}`"
                )

        elif key.endswith("_R"):
            pass

        elif key.endswith("__None"):
            target.uv_mode = "UV_IM_NIL"

    # Create bake targets
    for target in targets.values():
        if "basis" in target.name.lower():
            continue

        if target.name in [bt.name for bt in ht.bake_target_collection]:
            log.info("Skip existing bake target")
            continue

        new = ht.bake_target_collection.add()
        new.variant_collection.add()  # add default variant
        for key, value in iter_dc(target):
            setattr(new, key, value)

        target.bake_target = new

    def create_mirror(primary: int, secondary: int) -> BakeTargetMirrorEntry:
        new = ht.bake_target_mirror_collection.add()
        new.primary = primary
        new.secondary = secondary
        return new

    for mirror in mirror_list:
        create_mirror(
            ht.get_bake_target_index(mirror.primary.bake_target),
            ht.get_bake_target_index(mirror.secondary.bake_target),
        )


class BakeMirrors:
    def set_primary(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if mirror := ht.get_selected_mirror():
            if bake_target := ht.get_selected_bake_target():
                mirror.primary = ht.get_bake_target_index(bake_target)

    def set_secondary(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if mirror := ht.get_selected_mirror():
            if bake_target := ht.get_selected_bake_target():
                mirror.secondary = ht.get_bake_target_index(bake_target)

    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        GenericList.add(
            ht.bake_target_mirror_collection,
            AttrGet(ht, "selected_bake_target_mirror"),
            AttrSet(ht, "selected_bake_target_mirror"),
        )

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        GenericList.remove(
            ht.bake_target_mirror_collection,
            AttrGet(ht, "selected_bake_target_mirror"),
            AttrSet(ht, "selected_bake_target_mirror"),
        )


class BakeTargets:
    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        GenericList.add(
            ht.bake_target_collection,
            AttrGet(ht, "selected_bake_target"),
            AttrSet(ht, "selected_bake_target"),
        )

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        GenericList.remove(
            ht.bake_target_collection,
            AttrGet(ht, "selected_bake_target"),
            AttrSet(ht, "selected_bake_target"),
        )

    def edit_selected(operator: Operator, context: Context, ht: HomeomorphicProperties):
        bake_target = ht.get_selected_bake_target()
        if not bake_target:
            return

        bto = bake_target.get_object()
        if not bto:
            return

        work_scene = require_work_scene()
        set_scene(context, work_scene)
        view_layer = context.view_layer
        set_selection(view_layer.objects, bto)
        if bake_target.shape_key_name:
            bto.active_shape_key_index = bto.data.shape_keys.key_blocks.find(
                bake_target.shape_key_name
            )  # tech-note 4

        bpy.ops.object.mode_set(mode="EDIT")


class BakeGroups:
    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        GenericList.add(
            ht.bake_group_collection,
            AttrGet(ht, "selected_bake_group"),
            AttrSet(ht, "selected_bake_group"),
        )

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        GenericList.remove(
            ht.bake_group_collection,
            AttrGet(ht, "selected_bake_group"),
            AttrSet(ht, "selected_bake_group"),
        )

    class Members:
        def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
            if bake_group := ht.get_selected_bake_group():
                if bake_target := ht.get_selected_bake_target():
                    new = GenericList.add(
                        bake_group.members,
                        AttrGet(bake_group, "selected_member"),
                        AttrSet(bake_group, "selected_member"),
                    )
                    new.target = ht.get_bake_target_index(bake_target)

        def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
            if bake_group := ht.get_selected_bake_group():
                GenericList.remove(
                    bake_group.members,
                    AttrGet(bake_group, "selected_member"),
                    AttrSet(bake_group, "selected_member"),
                )


class BakeVariants:
    def add(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if bake_target := ht.get_selected_bake_target():
            GenericList.add(
                bake_target.variant_collection,
                AttrGet(bake_target, "selected_variant"),
                AttrSet(bake_target, "selected_variant"),
            )

    def remove(operator: Operator, context: Context, ht: HomeomorphicProperties):
        if bake_target := ht.get_selected_bake_target():
            GenericList.remove(
                bake_target.variant_collection,
                AttrGet(bake_target, "selected_variant"),
                AttrSet(bake_target, "selected_variant"),
            )


class FABA_OT_create_targets_from_avatar(FabaOperator):
    bl_label = "New bake targets from avatar mesh"
    bl_idname = "faba.create_targets_from_avatar_object"
    bl_description = "Create shape key targets from avatar mesh"
    faba_operator = create_targets_from_avatar_object
    faba_poll = poll_avatar_mesh


class FABA_OT_add_bake_target(FabaOperator):
    bl_label = "Add Baketarget"
    bl_description = "Create new bake target"
    bl_idname = "faba.add_bake_target"
    faba_operator = BakeTargets.add


class FABA_OT_show_selected_bt(FabaOperator):
    bl_label = "Edit selected"
    bl_description = "Edit selected bake target.\n" "Activates shape key as needed"
    bl_idname = "faba.show_selected_bt"
    faba_operator = BakeTargets.edit_selected


class FABA_OT_remove_bake_target(FabaOperator):
    bl_label = "Remove Selected"
    bl_description = "Remove selected bake target"
    bl_idname = "faba.remove_bake_target"
    faba_operator = BakeTargets.remove


class FABA_OT_add_bake_target_variant(FabaOperator):
    bl_label = "+"
    bl_description = "Add variant"
    bl_idname = "faba.add_bake_target_variant"
    faba_operator = BakeVariants.add


class FABA_OT_remove_bake_target_variant(FabaOperator):
    bl_label = "-"
    bl_description = "Remove mirror entry"
    bl_idname = "faba.remove_bake_target_variant"
    faba_operator = BakeVariants.remove


class FABA_OT_set_bake_mirror_primary(FabaOperator):
    bl_label = "Set primary"
    bl_description = "Set primary bake target of selected mirror entry"
    bl_idname = "faba.set_bake_mirror_primary"
    faba_operator = BakeMirrors.set_primary


class FABA_OT_set_bake_mirror_secondary(FabaOperator):
    bl_label = "Set secondary"
    bl_description = "Set secondary bake target of selected mirror entry"
    bl_idname = "faba.set_bake_mirror_secondary"
    faba_operator = BakeMirrors.set_secondary


class FABA_OT_add_bake_target_mirror(FabaOperator):
    bl_label = "+"
    bl_description = "Create new mirror entry"
    bl_idname = "faba.add_bake_target_mirror"
    faba_operator = BakeMirrors.add


class FABA_OT_remove_bake_target_mirror(FabaOperator):
    bl_label = "-"
    bl_description = "Remove mirror entry"
    bl_idname = "faba.remove_bake_target_mirror"
    faba_operator = BakeMirrors.remove


class FABA_OT_add_bake_group(FabaOperator):
    bl_label = "+"
    bl_description = "Create new bake group"
    bl_idname = "faba.add_bake_group"
    faba_operator = BakeGroups.add


class FABA_OT_remove_bake_group(FabaOperator):
    bl_label = "-"
    bl_description = "Remove selected bake group"
    bl_idname = "faba.remove_bake_group"
    faba_operator = BakeGroups.remove


class FABA_OT_add_bake_group_member(FabaOperator):
    bl_label = "+"
    bl_description = "Add selected bake target to bake group"
    bl_idname = "faba.add_bake_group_member"
    faba_operator = BakeGroups.Members.add


class FABA_OT_remove_bake_group_member(FabaOperator):
    bl_label = "-"
    bl_description = "Remove selected member from bake group"
    bl_idname = "faba.remove_bake_group_member"
    faba_operator = BakeGroups.Members.remove
