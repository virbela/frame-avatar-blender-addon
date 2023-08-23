import bpy
from bpy.types import Operator, Context

from .base import FabaOperator
from ..utils.helpers import require_bake_scene
from ..props import HomeomorphicProperties
from ..utils.bone_animation_viewer import view_animation


def clear_bake_targets(operator: Operator, context: Context, ht: HomeomorphicProperties):
    ht.selected_bake_target = -1
    while len(ht.bake_target_collection):
        ht.bake_target_collection.remove(0)

    ht.selected_bake_target_mirror = -1
    while len(ht.bake_target_mirror_collection):
        ht.bake_target_mirror_collection.remove(0)


def clear_bake_scene(operator: Operator, context: Context, ht: HomeomorphicProperties):
    scene = require_bake_scene()
    for item in scene.objects:
        if item.type == "MESH":
            bpy.data.meshes.remove(item.data, do_unlink=True)
        elif item.type == "ARMATURE":
            bpy.data.armatures.remove(item.data, do_unlink=True)


def debug_bone_animation(operator: Operator, context: Context, ht: HomeomorphicProperties):
    if ht.debug_animation_avatar_basis:
        ht.debug_animation_show = not ht.debug_animation_show

        if len(ht.debug_animation_actions):
            anim_name = ht.debug_animation_actions[0].name # First action is default animation
            for action in ht.debug_animation_actions:
                if action.checked:
                    anim_name = action.name
                    break
            view_animation(animation=anim_name, show=ht.debug_animation_show)


def start_debug_server(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bpy.ops.debug.connect_debugger_vscode()


def custom_op(operator: Operator, context: Context, ht: HomeomorphicProperties):
    """ Use this to run some custom testing/debug stuff
    """
    # -- show mirrors
    for bt in ht.bake_target_collection:
        print(f"{bt.bake_mode} \t{bt.name}")


class FABA_OT_clear_bake_scene(FabaOperator):
    bl_label =            "Remove everything from bake scene"
    bl_idname =           "faba.clear_bake_scene"
    bl_description =      "This is for internal development purposes and should not be seen in distribution"
    faba_operator =       clear_bake_scene


class FABA_OT_clear_bake_targets(FabaOperator):
    bl_label =            "Remove all bake targets"
    bl_idname =           "faba.clear_bake_targets"
    bl_description =      "Remove all the bake targets"
    faba_operator =       clear_bake_targets


class FABA_OT_show_bone_debug(FabaOperator):
    bl_label =            "Show bone animation debug"
    bl_idname =           "faba.debug_bone_animation"
    bl_description =      "This is for internal development purposes and should not be seen in distribution"
    faba_operator =       debug_bone_animation


class FABA_OT_start_debug_server(FabaOperator):
    bl_label =            "Start Debugger"
    bl_idname =           "faba.start_debugger"
    bl_description =      "This is for internal development purposes and should not be seen in distribution"
    faba_operator =       start_debug_server

class FABA_OT_custom_debug_operator(FabaOperator):
    bl_label =            "Custom Operator"
    bl_idname =           "faba.custom_operator"
    bl_description =      "This is for internal development purposes and should not be seen in distribution"
    faba_operator =       custom_op
