import os
import bpy 
import math
import bmesh
import numpy as np
from typing import List
from mathutils import Matrix
from bpy.types import Action, Context, Object

from .logging import log_writer as log
from .helpers import require_bake_scene, require_work_scene, get_gltf_export_indices


def generate_animation_shapekeys(context: Context, avatar: Object, animated_objects: List[Object]):
    scene = require_work_scene(context)
    HT = scene.homeomorphictools
    export_full_blob = all([ea.checked for ea in HT.export_animation_actions])

    armatures = [o for o in require_bake_scene(context).objects if o.type == 'ARMATURE']
    if len(armatures) > 1 or len(armatures) == 0:
        log.error("Expected a single armature in the bake scene")
        return

    filepath = bpy.data.filepath
    export_indices = get_gltf_export_indices(avatar)

    num_frames = get_num_frames()
    num_verts = len(export_indices)
    animation_buffer = np.zeros((num_verts * 3, num_frames, len(animated_objects)), dtype=np.float32)
    frame_counter = {o.name:0 for o in animated_objects}
    armature = armatures.pop()
    for action in bpy.data.actions:
        armature.animation_data.action = action
        export_action_animation(context, action, animated_objects, num_verts, export_indices)
        if export_full_blob:
            for oid, anim_obj in enumerate(animated_objects):
                meshes = get_per_frame_mesh(context, action, anim_obj)
                # -- add to blob file
                for mesh in meshes:
                    count = len(mesh.vertices)
                    buff = np.empty(count * 3, dtype=np.float64)
                    mesh.vertices.foreach_get('co', buff)
                    # duplicate by gltf verts
                    buff = buff.reshape((count, 3))[export_indices]
                    animation_buffer[:,frame_counter[anim_obj.name],oid] = buff.ravel()
                    frame_counter[anim_obj.name] += 1
                

                # XXX Deprecated Old Shapekey animation export
                # -- create shapekey in avatar
                # for frame, mesh in enumerate(meshes, start=1):
                #     sk_name = f'fabanim.{anim_obj.name}.{action.name}#{frame}'
                #     avatar.shape_key_add(name=sk_name, from_mix=False)
                #     shape_key_from_mesh(sk_name, avatar, mesh)
                [bpy.data.meshes.remove(me) for me in meshes]

    # reset frame
    context.scene.frame_set(1)
    if export_full_blob:
        directory = os.path.dirname(filepath)
        blob_file = open(os.path.join(directory, "animations.npy"), 'wb')
        np.save(blob_file, animation_buffer, allow_pickle=False)
        blob_file.close()


def get_per_frame_mesh(context: Context, action: Action, object: Object):
    meshes = []
    sx, sy = action.frame_range
    bakescene = require_bake_scene(context)
    if (sy - sx) > 1:
        # range stop is exclusive, so add one if animation has more than one frame
        sy += 1

    for i in range(int(sx), int(sy)):
        bakescene.frame_set(i)
        depsgraph = bakescene.view_layers[0].depsgraph

        eval_object = object.evaluated_get(depsgraph)
        me = bpy.data.meshes.new_from_object(eval_object)
        # -- convert coordinates from +Z up to +Y up
        me.transform(object.matrix_world @ Matrix.Rotation(math.radians(-90), 4, 'X'))
        meshes.append(me)
    return meshes


def get_vertex_data(meshes):
    result = []
    for me in meshes:
        result.append([v.copy() for v in me.vertices])
        if not me.users:
            bpy.data.meshes.remove(me)
    return result


def get_object_actions(obj: bpy.types.Object):
    actions = []
    for action in bpy.data.actions:
        if obj.user_of_id(action) > 0:
            actions.append(action)
    return actions


def shape_key_from_mesh(name, avatar, mesh):
    print('Generating animation shapekey..', name)
    bm = bmesh.new()
    bm.from_mesh(avatar.data)
    shape = bm.verts.layers.shape[name]

    for vert in bm.verts:
        vert[shape] = mesh.vertices[vert.index].co.copy()

    bm.to_mesh(avatar.data)
    bm.free()

    if not mesh.users:
        bpy.data.meshes.remove(mesh)

def get_num_frames():
    result = 0
    for action in bpy.data.actions:
        sx, sy = action.frame_range
        diff = sy - sx
        if diff > 1:
            # If more than one frame, the range is inclusive
            diff += 1

        result += diff
    return int(result)


def export_action_animation(context, action, animated_objects, num_verts, export_indices):
    scene = require_work_scene(context)
    HT = scene.homeomorphictools
    if action.name not in [ea.name for ea in HT.export_animation_actions]:
        # Possibly not a valid export action eg tpose
        return

    for export in HT.export_animation_actions:
        if export.name == action.name:
            if not export.checked:
                # This action is marked as do not export
                return

    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    blob_file = open(os.path.join(directory, f"{action.name}.npy"), 'wb')

    sx, sy = action.frame_range
    num_frames = sy - sx
    if num_frames > 1:
        # If more than one frame, the range is inclusive
        num_frames += 1

    animation_buffer = np.zeros((num_verts * 3, int(num_frames), len(animated_objects)), dtype=np.float32, order='F')
    for oid, anim_obj in enumerate(sorted(animated_objects, key=lambda o:o.name)):
        meshes = get_per_frame_mesh(context, action, anim_obj)
        # -- add to blob file
        for frame, mesh in enumerate(meshes):
            count = len(mesh.vertices)
            buff = np.empty(count * 3, dtype=np.float64)
            mesh.vertices.foreach_get('co', buff)
            # duplicate by gltf verts
            buff = buff.reshape((count, 3))[export_indices]
            animation_buffer[:,frame,oid] = buff.ravel()

        [bpy.data.meshes.remove(me) for me in meshes]
    np.save(blob_file, animation_buffer, allow_pickle=False)
