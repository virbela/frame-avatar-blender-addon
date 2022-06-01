import bpy 
import bmesh
from bpy.types import Action, Context, Object

from .helpers import require_bake_scene


def generate_vat_from_object(context: Context, object: Object):
    result = []
    actions = get_object_actions(object)
    vertex_count = len(object.data.vertices)
    for action in actions:
        meshes = get_per_frame_mesh(context, action, object)
        offsets = get_vertex_data(meshes)
        texture_size = vertex_count, int(action.frame_range.y - action.frame_range.x)
        tex = bake_vertex_data(f"{object.name}.{action.name}", offsets, texture_size)
        result.append(tex)
    # reset frame
    context.scene.frame_set(1)
    return result


def get_per_frame_mesh(context: Context, action: Action, object: Object):
    meshes = []
    sx, sy = action.frame_range
    object.animation_data.action = action
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
        
        me = bpy.data.meshes.new(f"{object.name}_{action.name}_animmesh{i}")
        bm.to_mesh(me)
        bm.free()
        me.calc_normals()
        meshes.append(me)
    return meshes


def get_vertex_data(meshes):
    """Return lists of vertex offsets and normals from a list of mesh data"""
    original = meshes[0].vertices
    offsets = []
    for me in reversed(meshes):
        for v in me.vertices:
            offset = v.co - original[v.index].co
            x, y, z = offset
            offsets.extend((x, y, z, 1))
        if not me.users:
            bpy.data.meshes.remove(me)
    return offsets


def bake_vertex_data(name, offsets, size):
    """Stores vertex offsets in seperate image textures"""
    width, height = size
    offset_texture = bpy.data.images.new(
        name=name,
        width=width,
        height=height,
        float_buffer=True
    )
    offset_texture.pixels = offsets
    return offset_texture


def get_object_actions(obj: bpy.types.Object):
    actions = []
    for action in bpy.data.actions:
        if obj.user_of_id(action) > 0:
            actions.append(action)
    return actions