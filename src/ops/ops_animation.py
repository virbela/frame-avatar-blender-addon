import bpy
from bpy.types import Operator, Context

from .base import FabaOperator
from ..props import HomeomorphicProperties
from ..utils.contextutils import selection
from ..utils.helpers import get_homeomorphic_tool_state


def transfer_skin_weights(
    operator: Operator, context: Context, ht: HomeomorphicProperties
):
    previous_mode = context.mode
    if previous_mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # -- clear all deformation vert groups from the target object
    for group in ht.transfer_skin_target.vertex_groups:
        if group.name.startswith("DEF-"):
            ht.transfer_skin_target.vertex_groups.remove(group)

    viewlayer = context.scene.view_layers[0]
    with selection(None, view_layer=viewlayer):
        # -- set source to active
        bpy.context.view_layer.objects.active = ht.transfer_skin_source

        # -- set target to selected
        ht.transfer_skin_target.select_set(True)

        # -- preform the data transfer
        bpy.ops.object.data_transfer(
            data_type="VGROUP_WEIGHTS",
            vert_mapping="NEAREST",
            layers_select_src="ALL",
            layers_select_dst="NAME",
        )

    # -- restore previous mode
    bpy.ops.object.mode_set(mode=previous_mode)


def poll_transfer_skin_weights(context: Context) -> bool:
    HT = get_homeomorphic_tool_state(context)
    return HT.transfer_skin_source and HT.transfer_skin_target


class FABA_OT_transfer_skin_weights(FabaOperator):
    bl_label = "Transfer Skin Weights"
    bl_idname = "faba.transfer_skin_weights"
    bl_description = "Transfer vertex groups from source object to target object"
    faba_operator = transfer_skin_weights
    faba_poll = poll_transfer_skin_weights
