import bpy
import typing
from bpy.types import (
    Operator,
    Context,
    ViewLayer,
    NodeTree,
    ShaderNodeTexImage,
    ShaderNodeOutputMaterial,
    ShaderNodeBsdfPrincipled,
)

from .base import FabaOperator
from ..utils.logging import log
from ..utils.exceptions import BakeException
from ..props import HomeomorphicProperties, BakeVariant, BakeTarget
from ..utils.helpers import require_bake_scene, set_scene, set_rendering, set_selection


def bake_all_bake_targets(
    operator: Operator, context: Context, ht: HomeomorphicProperties
) -> None:
    last_active_scene = context.scene
    bake_scene = require_bake_scene()
    view_layer = bake_scene.view_layers[0]  # TODO - make sure there is only one
    set_scene(context, bake_scene)

    for idx, bake_target in enumerate(ht.bake_target_collection, start=1):
        operator.report(
            {"INFO"}, f"Baking target {idx} / {len(ht.bake_target_collection)}."
        )
        log.info(f"Baking for {bake_target}")
        for variant in bake_target.variant_collection:
            bake_specific_variant(ht, view_layer, variant)
            # XXX bake cannot run as async here because of the loop, means we don't get
            # meaningful progress indicator
    run_bake(ht)
    set_scene(context, last_active_scene)


def bake_selected_bake_target(
    operator: Operator, context: Context, ht: HomeomorphicProperties
) -> None:
    last_active_scene = context.scene
    bake_scene = require_bake_scene()
    view_layer = bake_scene.view_layers[0]  # TODO - make sure there is only one
    set_scene(context, bake_scene)

    if bake_target := ht.get_selected_bake_target():
        if variant := bake_target.variant_collection[bake_target.selected_variant]:
            bake_specific_variant(ht, view_layer, variant)
            run_bake(ht)

    set_scene(context, last_active_scene)


def bake_selected_workmeshes(
    operator: Operator, context: Context, ht: HomeomorphicProperties
) -> None:
    bake_scene = require_bake_scene()
    view_layer = bake_scene.view_layers[0]  # TODO - make sure there is only one

    # NOTE - see technical detail 5 for further info on this temporary solution
    def get_bake_target_and_variant_from_workmesh(
        workmesh,
    ) -> typing.Tuple[BakeTarget, BakeVariant]:
        for bake_target in ht.bake_target_collection:
            for variant in bake_target.variant_collection:
                if variant.workmesh == workmesh:
                    return bake_target, variant

        raise BakeException.MissingBakeTargetVariant(workmesh)

    selection = list()
    for workmesh in view_layer.objects:
        if workmesh.select_get(view_layer=view_layer):
            selection.append(get_bake_target_and_variant_from_workmesh(workmesh))

    for _, variant in selection:
        workmesh = variant.workmesh

        ensure_color_output_node_ready(variant, workmesh.active_material.node_tree)

        # set active image in material
        material_nodes = workmesh.active_material.node_tree.nodes
        material_nodes.active = material_nodes["tex_target"]

        # set active UV index to source UV Map (since we want this in the final atlas)
        uv_layers = workmesh.data.uv_layers
        uv_layers.active = uv_layers[ht.baking_target_uvmap]

    run_bake(ht)


def bake_specific_variant(
    ht: HomeomorphicProperties, view_layer: ViewLayer, variant: BakeVariant
) -> None:
    workmesh = variant.workmesh

    ensure_color_output_node_ready(variant, workmesh.active_material.node_tree)

    set_rendering(view_layer.objects, workmesh)
    set_selection(
        view_layer.objects, workmesh, synchronize_active=True, make_sure_active=True
    )

    # set active image in material
    material_nodes = workmesh.active_material.node_tree.nodes
    material_nodes.active = material_nodes["tex_target"]

    # set active UV index to source UV Map (since we want this in the final atlas)
    uv_layers = workmesh.data.uv_layers
    uv_layers.active = uv_layers[ht.baking_target_uvmap]


def run_bake(ht: HomeomorphicProperties, invoke: bool = True) -> None:
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.render.bake.use_clear = False
    last_op = bpy.context.scene.render.bake.use_selected_to_active
    bpy.context.scene.render.bake.use_selected_to_active = False
    if ht.baking_options == "DIFFUSE":
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
    elif ht.baking_options == "COMBINED":
        bpy.context.scene.render.bake.use_pass_direct = True
        bpy.context.scene.render.bake.use_pass_indirect = True
        bpy.context.scene.render.bake.use_pass_diffuse = True
        bpy.context.scene.render.bake.use_pass_glossy = True
        bpy.context.scene.render.bake.use_pass_emit = True
        bpy.context.scene.render.bake.use_pass_transmission = True

    bpy.context.scene.view_settings.view_transform = "Standard"
    if invoke:
        bpy.ops.object.bake("INVOKE_DEFAULT", type=ht.baking_options)
    else:
        bpy.ops.object.bake(type=ht.baking_options)

    bpy.context.scene.render.bake.use_selected_to_active = last_op


def ensure_color_output_node_ready(variant: BakeVariant, tree: NodeTree) -> None:
    material_nodes = tree.nodes
    material_links = tree.links

    # ensure the texture output goes through diffusebsdf
    texnode = None
    for node in material_nodes:
        if isinstance(node, ShaderNodeTexImage):
            if node.image == variant.image:
                texnode = node
                break

    if not texnode:
        return

    outputnode = [
        n for n in material_nodes if isinstance(n, ShaderNodeOutputMaterial)
    ].pop()
    diffusenode = [
        n for n in material_nodes if isinstance(n, ShaderNodeBsdfPrincipled)
    ].pop()

    # remove all links from the texnode or the diffuse node
    for link in material_links:
        if link.from_node in [texnode, diffusenode]:
            tree.links.remove(link)

    # rebuild the links
    tree.links.new(texnode.outputs[0], diffusenode.inputs[0])
    tree.links.new(diffusenode.outputs[0], outputnode.inputs[0])


class FABA_OT_bake_selected_bake_target(FabaOperator):
    bl_label = "Bake selected target"
    bl_idname = "faba.bake_selected_bake_target"
    bl_description = "Bake textures for the selected bake target"
    faba_operator = bake_selected_bake_target


class FABA_OT_bake_selected_workmeshes(FabaOperator):
    bl_label = "Bake selected work meshes"
    bl_idname = "faba.bake_selected_workmeshes"
    bl_description = "Bake textures for selected work meshes"
    faba_operator = bake_selected_workmeshes


class FABA_OT_bake_all(FabaOperator):
    bl_label = "Bake all targets"
    bl_idname = "faba.bake_all"
    bl_description = "Bake textures for all targets and their variants"
    faba_operator = bake_all_bake_targets
