import bpy
import gpu
import numpy as np
from random import random
from gpu_extras.batch import batch_for_shader

from .bone_animation import BoneAnimationExporter

context = bpy.context

def view_animation(
        animation: str,
        shapekey_name: str):

    dns = bpy.app.driver_namespace
    if not dns.get('sd'):
        dns["sd"] = ShaderDrawer()

    sd = dns.get('sd')
    sd.remove()
    sd.update()


class ShaderDrawer:
    def __init__(self):
        self.handle = None

    def update(self):
        mesh = bpy.context.active_object.data
        mesh.calc_loop_triangles()

        vertices = np.empty((len(mesh.vertices), 3), 'f')
        indices = np.empty((len(mesh.loop_triangles), 3), 'i')

        mesh.vertices.foreach_get(
            "co", np.reshape(vertices, len(mesh.vertices) * 3))
        mesh.loop_triangles.foreach_get(
            "vertices", np.reshape(indices, len(mesh.loop_triangles) * 3))

        # -- green vis color
        vertex_colors = [(0, 1, 0, 1) for _ in range(len(mesh.vertices))]

        shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
        batch = batch_for_shader(
            shader, 'TRIS',
            {"pos": vertices, "color": vertex_colors},
            indices=indices,
        )

        def draw():
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.depth_mask_set(True)
            batch.draw(shader)
            gpu.state.depth_mask_set(False)


        self.handle = bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')

    def remove(self):
        if self.handle:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            except ValueError:
                pass