import bpy 
import bmesh

def generate_vat_from_mesh(context, object):

    data = bpy.data
    vertex_count = len(object.data.vertices)
    frame_count = len(frame_range(context.scene))

    meshes = get_per_frame_mesh_data(context, data, [object])
    export_mesh_data = meshes[0].copy()
    create_export_mesh_object(context, data, export_mesh_data)
    offsets, normals = get_vertex_data(data, meshes)
    texture_size = vertex_count, frame_count
    bake_vertex_data(context, data, offsets, normals, texture_size)

def get_per_frame_mesh_data(context, data, objects):
    """Return a list of combined mesh data per frame"""
    meshes = []
    for i in frame_range(context.scene):
        context.scene.frame_set(i)
        depsgraph = context.evaluated_depsgraph_get()
        bm = bmesh.new()
        for ob in objects:
            eval_object = ob.evaluated_get(depsgraph)
            me = data.meshes.new_from_object(eval_object)
            me.transform(ob.matrix_world)
            bm.from_mesh(me)
            data.meshes.remove(me)
        me = data.meshes.new("mesh")
        bm.to_mesh(me)
        bm.free()
        me.calc_normals()
        meshes.append(me)
    return meshes


def create_export_mesh_object(context, data, me):
    """Return a mesh object with correct UVs"""
    while len(me.uv_layers) < 2:
        me.uv_layers.new()
    uv_layer = me.uv_layers[1]
    uv_layer.name = "vertex_anim"
    for loop in me.loops:
        uv_layer.data[loop.index].uv = (
            (loop.vertex_index + 0.5)/len(me.vertices), 128/255
        )
    ob = data.objects.new("export_mesh", me)
    context.scene.collection.objects.link(ob)
    return ob


def get_vertex_data(data, meshes):
    """Return lists of vertex offsets and normals from a list of mesh data"""
    original = meshes[0].vertices
    offsets = []
    for me in reversed(meshes):
        for v in me.vertices:
            offset = v.co - original[v.index].co
            x, y, z = offset
            offsets.extend((x, -y, z, 1))
        if not me.users:
            data.meshes.remove(me)
    return offsets

def frame_range(scene):
    """Return a range object with with scene's frame start, end, and step"""
    return range(scene.frame_start, scene.frame_end, scene.frame_step)


def bake_vertex_data(name, data, offsets, size):
    """Stores vertex offsets and normals in seperate image textures"""
    width, height = size
    offset_texture = data.images.new(
        name=name,
        width=width,
        height=height,
        alpha=True,
        float_buffer=True
    )
    offset_texture.pixels = offsets
