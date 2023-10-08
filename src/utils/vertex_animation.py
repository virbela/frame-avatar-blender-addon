import os
import bpy
import math
import numpy as np
from pathlib import Path
from mathutils import Matrix
from bpy.types import Action, Context, Object, Mesh

from .constants import GLB_VERT_COUNT
from .logging import log
from .helpers import (
    get_prefs,
    popup_message,
    require_bake_scene,
    get_action_frame_range,
    get_gltf_export_indices,
    get_num_frames_all_actions,
    get_homeomorphic_tool_state,
    get_num_frames_single_action,
)


def generate_animation_blob(
    context: Context, avatar: Object, animated_objects: list[Object]
) -> None:
    HT = get_homeomorphic_tool_state(context)
    export_full_blob = all([ea.checked for ea in HT.export_animation_actions])

    filepath = bpy.data.filepath
    export_indices = get_gltf_export_indices(avatar)

    prefs = get_prefs()
    if prefs.custom_frame_validation:
        # XXX Hard check for frame vert coung
        if len(export_indices) != GLB_VERT_COUNT:
            log.error("Invalid vert count for animations")

    num_frames = get_num_frames_all_actions()
    num_verts = len(export_indices)
    animation_buffer = np.zeros(
        (num_verts * 3, num_frames, len(animated_objects)), dtype=np.float32
    )
    frame_counter = {o.name: 0 for o in animated_objects}
    armature = HT.avatar_rig
    for action in bpy.data.actions:
        armature.animation_data.action = action
        export_action_animation(
            context, action, animated_objects, num_verts, export_indices
        )
        if export_full_blob:
            for oid, anim_obj in enumerate(animated_objects):
                meshes = get_per_frame_mesh(context, action, anim_obj)
                # -- add to blob file
                for mesh in meshes:
                    count = len(mesh.vertices)
                    buff = np.empty(count * 3, dtype=np.float64)
                    mesh.vertices.foreach_get("co", buff)
                    # duplicate by gltf verts
                    buff = buff.reshape((count, 3))[export_indices]
                    animation_buffer[
                        :, frame_counter[anim_obj.name], oid
                    ] = buff.ravel()
                    frame_counter[anim_obj.name] += 1

                # XXX Deprecated Old Shapekey animation export
                # -- create shapekey in avatar
                # for frame, mesh in enumerate(meshes, start=1):
                #     sk_name = f"fabanim.{anim_obj.name}.{action.name}#{frame}"
                #     avatar.shape_key_add(name=sk_name, from_mix=False)
                #     shape_key_from_mesh(sk_name, avatar, mesh)
                [bpy.data.meshes.remove(me) for me in meshes]

    # reset frame
    context.scene.frame_set(1)
    if export_full_blob:
        directory = os.path.dirname(filepath)
        blob_file = open(os.path.join(directory, "animations.npy"), "wb")
        np.save(blob_file, animation_buffer, allow_pickle=False)
        blob_file.close()


def get_per_frame_mesh(context: Context, action: Action, object: Object) -> list[Mesh]:
    meshes = []
    bakescene = require_bake_scene()
    for i in range(*get_action_frame_range(action)):
        bakescene.frame_set(i)
        depsgraph = bakescene.view_layers[0].depsgraph

        eval_object = object.evaluated_get(depsgraph)
        me = bpy.data.meshes.new_from_object(eval_object)
        # -- convert coordinates from +Z up to +Y up
        me.transform(object.matrix_world @ Matrix.Rotation(math.radians(-90), 4, "X"))
        meshes.append(me)
    return meshes


def export_action_animation(
    context: Context,
    action: Action,
    animated_objects: list[Object],
    num_verts: int,
    export_indices: list[int],
) -> None:
    HT = get_homeomorphic_tool_state(context)
    if action.name not in [ea.name for ea in HT.export_animation_actions]:
        # Possibly not a valid export action eg tpose
        return

    for export in HT.export_animation_actions:
        if export.name == action.name:
            if not export.checked:
                # This action is marked as do not export
                return

    prefs = get_prefs()
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    if os.path.exists(prefs.npy_export_dir):
        directory = str(Path(prefs.npy_export_dir).absolute())
    blob_file = open(os.path.join(directory, f"{action.name}.npy"), "wb")

    num_frames = get_num_frames_single_action(action)
    animation_buffer = np.zeros(
        (num_verts * 3, int(num_frames), len(animated_objects)),
        dtype=np.float32,
        order="F",
    )
    for oid, anim_obj in enumerate(sorted(animated_objects, key=lambda o: o.name)):
        meshes = get_per_frame_mesh(context, action, anim_obj)
        # -- add to blob file
        for frame, mesh in enumerate(meshes):
            count = len(mesh.vertices)
            buff = np.empty(count * 3, dtype=np.float64)
            mesh.vertices.foreach_get("co", buff)
            # duplicate by gltf verts
            buff = buff.reshape((count, 3))[export_indices]
            animation_buffer[:, frame, oid] = buff.ravel()

        [bpy.data.meshes.remove(me) for me in meshes]
    np.save(blob_file, animation_buffer, allow_pickle=False)


def validate_animation_export_verts(avatar: Object) -> bool:
    export_indices = get_gltf_export_indices(avatar)
    if len(export_indices) != GLB_VERT_COUNT:
        log.error(
            f"Invalid GLB vert count. \nExpected {GLB_VERT_COUNT} got {len(export_indices)}. Ensure base avatar mesh has no materials and only 2 uv layers"
        )
        popup_message(
            "Invalid GLB vert count. See console for more details", "Export Error"
        )
        return False
    return True
