import bpy
import unittest

from src.utils import vertex_animation


class TestUtilsAnimation(unittest.TestCase):
    def test_get_per_frame_mesh(self) -> None:
        obj = bpy.data.objects["Cube"]

        # single frame action
        obj.keyframe_insert("location", frame=1)
        meshes = vertex_animation.get_per_frame_mesh(
            bpy.context, obj.animation_data.action, obj
        )
        self.assertEqual(len(meshes), 1)

        # multi frame action
        obj.keyframe_insert("location", frame=100)
        meshes = vertex_animation.get_per_frame_mesh(
            bpy.context, obj.animation_data.action, obj
        )
        self.assertEqual(len(meshes), 100)

    def test_gltf_export_indices(self) -> None:
        obj = bpy.data.objects["Cube"]
        indices = vertex_animation.get_gltf_export_indices(obj)
        self.assertEqual(len(indices), 14)
