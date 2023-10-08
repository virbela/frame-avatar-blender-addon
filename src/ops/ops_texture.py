import bpy
import bmesh
from bpy.types import Context, Operator, Object, Scene, Image

from .base import FabaOperator
from ..utils.constants import TARGET_UV_MAP
from ..utils.structures import Intermediate
from ..utils.logging import log
from ..props import HomeomorphicProperties
from .common import set_uv_map, GuardedOperator
from ..utils.helpers import (
    set_scene,
    set_active,
    set_selection,
    clear_selection,
    NamedEntryAction,
    create_named_entry,
    require_bake_scene,
)


def UVPM2_INSTALLED() -> bool:
    return "uvpackmaster2" in dir(bpy.ops)


def UVPM3_INSTALLED() -> bool:
    return "uvpackmaster3" in dir(bpy.ops)


def UVPM_INSTALLED() -> bool:
    return UVPM2_INSTALLED() or UVPM3_INSTALLED()


def auto_assign_atlas(
    operator: Operator, context: Context, ht: HomeomorphicProperties
) -> None:
    """Goes through all bake targets and assigns them to the correct
    intermediate atlas and UV set based on the uv_mode"""

    # TODO - currently we don't take into account that variants may end up on
    # different bins which is fine but we need to store the intermediate target
    # with the variant and not the bake target
    # TODO - currently we will just hardcode the intermediate atlases but later we
    # need to check which to use and create them if needed
    a_width = ht.atlas_size
    a_height = ht.atlas_size

    atlas_color = create_named_entry(
        bpy.data.images,
        "atlas_intermediate_color",
        a_width,
        a_height,
        action=NamedEntryAction.GET_EXISTING,
    )
    atlas_red = create_named_entry(
        bpy.data.images,
        "atlas_intermediate_red",
        a_width,
        a_height,
        action=NamedEntryAction.GET_EXISTING,
    )
    atlas_green = create_named_entry(
        bpy.data.images,
        "atlas_intermediate_green",
        a_width,
        a_height,
        action=NamedEntryAction.GET_EXISTING,
    )
    atlas_blue = create_named_entry(
        bpy.data.images,
        "atlas_intermediate_blue",
        a_width,
        a_height,
        action=NamedEntryAction.GET_EXISTING,
    )

    for at in [atlas_blue, atlas_green, atlas_red, atlas_color]:
        if len(at.pixels) == 0:
            # image data disappered, rebuild
            name = at.name
            bpy.data.images.remove(at)
            at = bpy.data.images.new(name, a_width, a_height)

        at.generated_color = (1.0, 1.0, 1.0, 1.0)
        if tuple(at.size) != (a_width, a_height):
            at.scale(a_width, a_height)
            at.update()

    # TODO - here we need to put things in bins like how the UV packing does below
    # but before we can do this we should look at the variants
    # TBD - should we do it all from beginning? for now yes -
    # maybe later we can have selection

    # TO-DOC - document what happens here properly

    uv_object_list = get_intermediate_uv_object_list(ht)

    monochrome_targets = list()
    color_targets = list()
    nil_targets = list()
    frozen_targets = list()
    for uv in uv_object_list:
        if uv.bake_target.uv_mode == "UV_IM_MONOCHROME":
            monochrome_targets.append(uv)
        elif uv.bake_target.uv_mode == "UV_IM_COLOR":
            color_targets.append(uv)
        elif uv.bake_target.uv_mode == "UV_IM_NIL":
            nil_targets.append(uv)
        elif uv.bake_target.uv_mode == "UV_IM_FROZEN":
            frozen_targets.append(uv)
        else:
            raise Exception(uv.bake_target.uv_mode)  # TODO proper exception

    log.debug(
        f"UV bins - monochrome: {len(monochrome_targets)}, color: {len(color_targets)}, nil: {len(nil_targets)}, frozen: {len(frozen_targets)}"
    )

    # NOTE - we support multiple color bins but it is not used yet
    color_bins = [
        Intermediate.Packing.AtlasBin(
            "color", atlas=bpy.data.images["atlas_intermediate_color"]
        ),
    ]

    mono_bins = [
        Intermediate.Packing.AtlasBin(
            "red", atlas=bpy.data.images["atlas_intermediate_red"]
        ),
        Intermediate.Packing.AtlasBin(
            "green", atlas=bpy.data.images["atlas_intermediate_green"]
        ),
        Intermediate.Packing.AtlasBin(
            "blue", atlas=bpy.data.images["atlas_intermediate_blue"]
        ),
    ]

    all_targets = [
        (monochrome_targets, mono_bins),
        (color_targets, color_bins),
    ]

    def get_channel_from_bin(atlas_bin: Intermediate.Packing.AtlasBin) -> str:
        if atlas_bin.name == "color":
            return "UV_TARGET_COLOR"
        elif atlas_bin.name == "red":
            return "UV_TARGET_R"
        elif atlas_bin.name == "green":
            return "UV_TARGET_G"
        elif atlas_bin.name == "blue":
            return "UV_TARGET_B"
        return "UV_TARGET_NIL"

    for target_list, bin_list in all_targets:
        for uv_island in sorted(
            target_list, reverse=True, key=lambda island: island.area
        ):
            uv_island.bin = target_bin = min(bin_list, key=lambda bin: bin.allocated)
            uv_island.variant.intermediate_atlas = target_bin.atlas
            uv_island.variant.uv_target_channel = get_channel_from_bin(target_bin)
            target_bin.allocated += uv_island.area


def pack_uv_islands(
    operator: Operator, context: Context, ht: HomeomorphicProperties
) -> None:
    last_active_scene = context.scene

    bake_scene = require_bake_scene()
    set_scene(context, bake_scene)

    all_uv_object_list = get_intermediate_uv_object_list(ht)
    mono_box = (0.0, 1.0, 1.0, ht.color_percentage / 100.0)
    color_box = (0.0, 0.0, 1.0, ht.color_percentage / 100.0)

    pack_intermediate_atlas(
        bake_scene,
        all_uv_object_list,
        bpy.data.images["atlas_intermediate_red"],
        TARGET_UV_MAP,
        mono_box,
    )
    pack_intermediate_atlas(
        bake_scene,
        all_uv_object_list,
        bpy.data.images["atlas_intermediate_green"],
        TARGET_UV_MAP,
        mono_box,
    )
    pack_intermediate_atlas(
        bake_scene,
        all_uv_object_list,
        bpy.data.images["atlas_intermediate_blue"],
        TARGET_UV_MAP,
        mono_box,
    )
    pack_intermediate_atlas(
        bake_scene,
        all_uv_object_list,
        bpy.data.images["atlas_intermediate_color"],
        TARGET_UV_MAP,
        color_box,
    )

    set_scene(context, last_active_scene)


def get_intermediate_uv_object_list(
    ht: HomeomorphicProperties,
) -> list[Intermediate.Packing.BakeTarget]:
    uv_object_list = list()

    for bake_target in ht.bake_target_collection:
        if bake_target.bake_mode == "UV_BM_REGULAR":
            for variant_name, variant in bake_target.iter_variants():
                if not variant.workmesh:
                    continue

                mesh = bmesh.new()
                mesh.from_mesh(variant.workmesh.data)
                uv_area = sum(
                    face.calc_area() * bake_target.uv_area_weight for face in mesh.faces
                )
                mesh.free()

                uv_object_list.append(
                    Intermediate.Packing.BakeTarget(
                        bake_target, variant, uv_area, variant_name
                    )
                )

    return uv_object_list


def pack_intermediate_atlas(
    bake_scene: Scene,
    all_uv_object_list: list[Intermediate.Packing.BakeTarget],
    atlas: Image,
    uv_map: str,
    box: tuple[float, float, float, float]
) -> None:
    view_layer = bake_scene.view_layers[0]

    uv_object_list = [
        u for u in all_uv_object_list if u.variant.intermediate_atlas == atlas
    ]
    if not uv_object_list:
        # XXX nothing todo for this atlas
        log.info(f"Missing UV object list for {atlas.name}!")
        return

    for uv_island in uv_object_list:
        scale_factor = uv_island.area * uv_island.bake_target.uv_area_weight
        copy_and_transform_uv(
            uv_island.bake_target.source_object,
            uv_island.bake_target.source_uv_map,
            uv_island.variant.workmesh,
            uv_map,
            scale_factor,
        )
    # ensure meshes are not hidden
    for obl in uv_object_list:
        obl.variant.workmesh.hide_set(False)

    # TO-FIX skipping partitioning object temporarily
    set_selection(view_layer.objects, *(u.variant.workmesh for u in uv_object_list))
    # set first to active since we need an arbritary active object
    set_active(view_layer.objects, uv_object_list[0].variant.workmesh)

    # enter edit mode and select all faces and UVs
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")  # Select faces in model editor
    bpy.ops.uv.select_all(action="SELECT")  # Select UVs in UV editor

    if UVPM2_INSTALLED():
        disable_packing_box = GuardedOperator(bpy.ops.uvpackmaster2.disable_target_box)
        enable_packing_box = GuardedOperator(bpy.ops.uvpackmaster2.enable_target_box)

        bpy.ops.uvpackmaster2.split_overlapping_islands()
        bake_scene.uvp2_props.rot_step = 45

        # note - we use guarded operators for setting the state of the packing box
        # since setting it to the same state it already is will fail
        disable_packing_box()

        if box:
            (
                bake_scene.uvp2_props.target_box_p1_x,
                bake_scene.uvp2_props.target_box_p1_y,
                bake_scene.uvp2_props.target_box_p2_x,
                bake_scene.uvp2_props.target_box_p2_y,
            ) = box

            enable_packing_box()

        # NOTE - if we later do downsampling when doing final bake - we must consider
        # the final pixel margin and not the intermediate one!
        bake_scene.uvp2_props.pixel_margin = 5  # TODO - not hardcode! We could just not
        # set this and set it in UVP UI but I think it is better this is a setting
        # in FABA so that we don't forget about it

        bpy.ops.uvpackmaster2.uv_pack()
        disable_packing_box()
    elif UVPM3_INSTALLED():
        # Not working in UVPM3
        # bpy.ops.uvpackmaster3.split_overlapping()
        bake_scene.uvpm3_props.rotation_step = 45

        if box:
            bake_scene.uvpm3_props.custom_target_box_enable = True
            (
                bake_scene.uvpm3_props.custom_target_box.p1_x,
                bake_scene.uvpm3_props.custom_target_box.p1_y,
                bake_scene.uvpm3_props.custom_target_box.p2_x,
                bake_scene.uvpm3_props.custom_target_box.p2_y,
            ) = box

        # NOTE - if we later do downsampling when doing final bake
        #     - we must consider the final pixel margin and not the intermediate one!
        # TODO(ranjian0) - dont hardcode pixel margin!
        bake_scene.uvpm3_props.pixel_margin_enable = True
        bake_scene.uvpm3_props.pixel_margin = 5
        bpy.ops.uvpackmaster3.pack(mode_id="pack.single_tile")
    else:
        # TODO(ranjian0) Find a way to box pack with default blender packer.
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=0.01)

    clear_selection(view_layer.objects)
    bpy.ops.object.mode_set(mode="OBJECT")


def copy_and_transform_uv(
    source_object: Object,
    source_layer: str,
    target_object: Object,
    target_layer: str,
    scale_factor: float = 1.0,
):
    # TODO - investigate if we can get uv layer index without actually changing it and
    # getting mesh.loops.layers.uv.active
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        # No need, context already set
        pass

    # TODO - would be great if we made a context manager for these commands so that we
    # could reset all changes when exiting the context (this applies to a lot of
    # things outside this function too)
    set_uv_map(source_object, source_layer)
    set_uv_map(target_object, target_layer)

    source_mesh = bmesh.new()
    source_mesh.from_mesh(source_object.data)
    source_uv_layer_index = source_mesh.loops.layers.uv.active

    target_mesh = bmesh.new()
    target_mesh.from_mesh(target_object.data)
    target_uv_layer_index = target_mesh.loops.layers.uv.active

    # TODO - use a strict zip here so we can detect error and also handle any such
    # errors using the .free() methods in the finalization handler
    for source_face, target_face in zip(source_mesh.faces, target_mesh.faces):
        for source_loop, target_loop in zip(source_face.loops, target_face.loops):
            source_uv = source_loop[source_uv_layer_index].uv
            target_loop[target_uv_layer_index].uv = source_uv * scale_factor

    target_mesh.to_mesh(target_object.data)
    source_mesh.free()
    target_mesh.free()


class FABA_OT_auto_assign_atlas(FabaOperator):
    bl_label = "Auto assign atlas/UV"
    bl_idname = "faba.auto_assign_atlas"
    bl_description = "Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
    faba_operator = auto_assign_atlas


class FABA_OT_pack_uv_islands(FabaOperator):
    bl_label = "Pack UV islands"
    bl_idname = "faba.pack_uv_islands"
    bl_description = (
        "Go through the bake targets and pack workmesh uvs into intermediate atlases"
    )
    faba_operator = pack_uv_islands
