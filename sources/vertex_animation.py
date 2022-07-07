import bpy 
import bmesh
from typing import List
from bpy.types import Action, Context, Object

from .logging import log_writer as log
from .helpers import require_bake_scene


def generate_animation_shapekeys(context: Context, avatar: Object, animated_objects: List[Object]):
    armatures = [o for o in require_bake_scene(context).objects if o.type == 'ARMATURE']
    if len(armatures) > 1 or len(armatures) == 0:
        log.error("Expected a single armature in the bake scene")
        return

    armature = armatures.pop()
    for action in bpy.data.actions:
        armature.animation_data.action = action
        for anim_obj in animated_objects:
            meshes = get_per_frame_mesh(context, action, anim_obj)
            # -- create shapekey in avatar
            for frame, mesh in enumerate(meshes, start=1):
                sk_name = f'fabanim.{anim_obj.name}.{action.name}#{frame}'
                avatar.shape_key_add(name=sk_name, from_mix=False)
                shape_key_from_mesh(sk_name, avatar, mesh)

    # reset frame
    context.scene.frame_set(1)


def get_per_frame_mesh(context: Context, action: Action, object: Object):
    meshes = []
    sx, sy = action.frame_range
    bakescene = require_bake_scene(context)

    # range stop is exclusive, so add one
    for i in range(int(sx), int(sy + 1)):
        bakescene.frame_set(i)
        depsgraph = bakescene.view_layers[0].depsgraph

        bm = bmesh.new()
        eval_object = object.evaluated_get(depsgraph)
        me = bpy.data.meshes.new_from_object(eval_object)
        me.transform(object.matrix_world)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        
        me = bpy.data.meshes.new(f"fabanim.{object.name}.{action.name}#{i}")
        bm.to_mesh(me)
        bm.free()
        me.calc_normals()
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
