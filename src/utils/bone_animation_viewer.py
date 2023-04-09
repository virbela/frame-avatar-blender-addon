import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader

from .bone_animation import BoneAnimationExporter
from .helpers import get_asset_file, get_homeomorphic_tool_state, is_dev

context = bpy.context

def view_animation(animation: str, show: bool):
    ht = get_homeomorphic_tool_state(bpy.context)

    dns = bpy.app.driver_namespace
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
        self.animation_data = BoneAnimationExporter(bpy.context, ht)

    def update(self):
        mesh = self.ht.avatar_mesh.data
        mesh.calc_loop_triangles()

        vertices = np.empty((len(mesh.vertices), 3), 'f')
        indices = np.empty((len(mesh.loop_triangles), 3), 'i')

        mesh.vertices.foreach_get(
            "co", np.reshape(vertices, len(mesh.vertices) * 3))
        mesh.loop_triangles.foreach_get(
            "vertices", np.reshape(indices, len(mesh.loop_triangles) * 3))


        vertexshader = get_asset_file("bone_animation.vert.glsl", 'r')
        fragmentshader = get_asset_file("bone_animation.frag.glsl", 'r')
        shader = gpu.types.GPUShader(vertexshader, fragmentshader)
        batch = batch_for_shader(
            shader, 'TRIS',
            {"position": vertices},
            indices=indices,
        )

        def draw():
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.depth_mask_set(True)
            shader.bind()
            shader.uniform_float("model", self.ht.avatar_mesh.matrix_world)
            shader.uniform_float("view", bpy.context.region_data.view_matrix)
            shader.uniform_float("projection", bpy.context.region_data.window_matrix)
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
if is_dev():
    print("Resetting Bone Animation ShaderDrawer...")
    try:
        del bpy.app.driver_namespace['sd']
    except KeyError:
        pass