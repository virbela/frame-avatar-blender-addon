import bpy 
import uuid
import bmesh
import numpy
from bpy.types import Action, Context, Object

def generate_vat_from_object(context: Context, object: Object):
    result = []
    actions = get_object_actions(object)
    vertex_count = len(object.data.vertices)
    for action in actions:
        meshes = get_per_frame_mesh(context, action, object)

        export_mesh_data = meshes[0].copy()
        create_export_mesh_object(context, export_mesh_data)

        offsets = get_vertex_data(meshes)
        texture_size = vertex_count, action.frame_range.y - action.frame_range.x
        tex = bake_vertex_data(action.name, offsets, texture_size)
        result.append(tex)
    return result


def get_per_frame_mesh(context: Context, action: Action, object: Object):
    meshes = []
    for i in range(*tuple(map(int, action.frame_range))):
        context.scene.frame_set(i)
        depsgraph = context.evaluated_depsgraph_get()
        bm = bmesh.new()        
        eval_object = object.evaluated_get(depsgraph)
        me = bpy.data.meshes.new_from_object(eval_object)
        me.transform(object.matrix_world)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        me = bpy.data.meshes.new("mesh")
        bm.to_mesh(me)
        bm.free()
        me.calc_normals()
        meshes.append(me)
    return meshes


def create_export_mesh_object(context, me):
    """Return a mesh object with correct UVs"""
    while len(me.uv_layers) < 2:
        me.uv_layers.new()
    uv_layer = me.uv_layers[1]
    uv_layer.name = f"vertex_anim_{uuid.uuid4()}"
    for loop in me.loops:
        uv_layer.data[loop.index].uv = (
            (loop.vertex_index + 0.5)/len(me.vertices), 128/255
        )
    ob = bpy.data.objects.new(f"export_mesh_{uuid.uuid4()}", me)
    context.scene.collection.objects.link(ob)
    return ob


def get_vertex_data(meshes):
    """Return lists of vertex offsets and normals from a list of mesh data"""
    original = meshes[0].vertices
    offsets = []
    for me in reversed(meshes):
        for v in me.vertices:
            offset = v.co - original[v.index].co
            x, y, z = offset
            offsets.extend((x, y, z))
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
    
    offset_texture.pixels = numpy.array(offsets, dtype=numpy.float16)
    return offset_texture


def get_object_actions(obj: bpy.types.Object):
    actions = []
    for action in bpy.data.actions:
        if obj.user_of_id(action) > 0:
            actions.append(action)
    return actions