import bpy
import gpu
import time
import bmesh
import numpy as np
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
        dns["sd"] = ShaderDrawer(ht, animation)

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
    def __init__(self, ht, action):
        self.ht = ht
        self.handle = None
        self.action = action
        self.animation_data: BoneAnimationExporter = bpy.app.driver_namespace['be']

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
            
            bone_weights = []
            bone_indices = []
            weights = self.animation_data.weights[skname]
            for vert in bm.verts:
                bone_map = list(enumerate(weights[str(vert.index)]))
                top_four = sorted(bone_map, key=lambda v:v[1])[-4:]
                bi = tuple(v[0] for v in top_four)
                bw = tuple(v[1] for v in top_four)
                bone_indices.append(bi)
                bone_weights.append(bw)
            bm.free()

            num_verts = len(vertices)
            colors_tri = [(0, 1, 0, 1) for _ in range(num_verts)]
            colors_vert = [(0, 0, 0, 1) for _ in range(num_verts)]

            fmt = gpu.types.GPUVertFormat()
            fmt.attr_add(id="position", comp_type='F32', len=3, fetch_mode='FLOAT')
            fmt.attr_add(id="color", comp_type='F32', len=4, fetch_mode='FLOAT')
            fmt.attr_add(id="bone_weights", comp_type='F32', len=4, fetch_mode='FLOAT')
            fmt.attr_add(id="bone_indices", comp_type='F32', len=4, fetch_mode='FLOAT')

            vbo = gpu.types.GPUVertBuf(format=fmt, len=num_verts)
            vbo.attr_fill(id="position", data=vertices)
            vbo.attr_fill(id="color", data=colors_tri)
            vbo.attr_fill(id="bone_weights", data=bone_weights)
            vbo.attr_fill(id="bone_indices", data=bone_indices)

            vbo_vert = gpu.types.GPUVertBuf(format=fmt, len=num_verts)
            vbo_vert.attr_fill(id="position", data=vertices)
            vbo_vert.attr_fill(id="color", data=colors_vert)
            vbo_vert.attr_fill(id="bone_weights", data=bone_weights)
            vbo_vert.attr_fill(id="bone_indices", data=bone_indices)

            ibo = gpu.types.GPUIndexBuf(type='TRIS', seq=indices)

            batch = gpu.types.GPUBatch(type='TRIS', buf=vbo, elem=ibo)
            batch_verts = gpu.types.GPUBatch(type='POINTS', buf=vbo_vert, elem=ibo)
            batches.extend([batch_verts])
        return batches



    def update(self):

        # -- shader sources
        vertex_source = get_asset_file("bone_animation.vert.glsl", 'r')
        fragment_source = get_asset_file("bone_animation.frag.glsl", 'r')

        shader = gpu.types.GPUShader(vertex_source, fragment_source, name="BoneAnimationShader")
        batches = self.make_mesh_batches(shader)

        bone_transforms = self.animation_data.transforms[self.action]
        num_frames = len(bone_transforms)

        def draw():
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.depth_mask_set(True)
            shader.bind()

            frame = int(time.time() % num_frames)
            transforms = bone_transforms[frame]
            shader.uniform_vector_float(
                shader.uniform_from_name("bones"),
                np.array(transforms), 16, 31
            )

            mvp = (
                context.region_data.window_matrix @
                context.region_data.view_matrix
            )
            shader.uniform_float("mvp", mvp)
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
        sd = bpy.app.driver_namespace['sd']
        sd.remove() 
        del bpy.app.driver_namespace['sd']
    except KeyError:
        pass

    # del bpy.app.driver_namespace['be']