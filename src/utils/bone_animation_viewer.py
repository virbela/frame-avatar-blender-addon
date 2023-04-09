import bpy
import gpu
import bmesh
from gpu_extras.batch import batch_for_shader

from .bone_animation import BoneAnimationExporter
from .helpers import get_asset_file, get_homeomorphic_tool_state, is_dev

context = bpy.context

ANIMATED_SHAPE_KEYS = [
    "Body_Human",
    "Arm_L",
    "Arm_R",
    "Formal_pants_L",
    "Formal_pants_R"
]

def view_animation(animation: str, show: bool):
    ht = get_homeomorphic_tool_state(bpy.context)

    dns = bpy.app.driver_namespace
    if not dns.get('be'):
        dns['be'] = BoneAnimationExporter(bpy.context, ht)

    if not dns.get('sd'):
        dns["sd"] = ShaderDrawer(ht)

    sd = dns.get('sd')
    sd.remove()
    if show:
        sd.update()
    Update3DViewPorts()


def Update3DViewPorts():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

class ShaderDrawer:
    def __init__(self, ht):
        self.ht = ht
        self.handle = None
        self.animation_data = bpy.app.driver_namespace['be']

    def make_mesh_batches(self, shader):
        batches = []
        mesh = self.ht.avatar_mesh.data

        for skname in ANIMATED_SHAPE_KEYS:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            shape = bm.verts.layers.shape[skname]

            vertices = []
            bm.verts.ensure_lookup_table()
            for v in bm.verts:
                vertices.append(v[shape].to_tuple(3))
            
            indices = []
            bm.faces.ensure_lookup_table()
            for f in bm.faces:
                indices.append([v.index for v in f.verts])
            bm.free()

            batch = batch_for_shader(
                shader, 'TRIS',
                {"position": vertices, "color": [(0, 1, 0, 1) for _ in range(len(vertices))]},
                indices=indices,
            )

            batch_verts = batch_for_shader(
                shader, 'POINTS',
                {"position": vertices, "color": [(0, 0, 0, 1) for _ in range(len(vertices))]}
            )

            batches.extend([batch, batch_verts])
        return batches



    def update(self):

        vertexshader = get_asset_file("bone_animation.vert.glsl", 'r')
        fragmentshader = get_asset_file("bone_animation.frag.glsl", 'r')
        shader = gpu.types.GPUShader(vertexshader, fragmentshader)

        batches = self.make_mesh_batches(shader)

        def draw():
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.depth_mask_set(True)
            shader.bind()
            shader.uniform_float("model", self.ht.avatar_mesh.matrix_world)
            shader.uniform_float("view", context.region_data.view_matrix)
            shader.uniform_float("projection", context.region_data.window_matrix)
            for batch in batches:
                batch.draw(shader)
            gpu.state.depth_mask_set(False)


        self.handle = bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')

    def remove(self):
        if self.handle:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            except ValueError:
                pass

# Dev only
# Destroy the shader drawer on scriptwatcher reload
if is_dev() and 1:
    print("Resetting Bone Animation ShaderDrawer...")
    try:
        del bpy.app.driver_namespace['sd']
    except KeyError:
        pass