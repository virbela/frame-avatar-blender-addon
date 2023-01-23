import bpy
import unittest

from src.utils import animation

class TestUtilsAnimation(unittest.TestCase):
    def test_get_num_frames(self):
        self.assertEqual(animation.get_num_frames(), 0)

        action = bpy.data.actions.new('test_action')
        action.use_frame_range = True
        action.frame_start = 1
        action.frame_end = 100

        action = bpy.data.actions.new('test_action2')
        action.use_frame_range = True
        action.frame_start = 1
        action.frame_end = 30

        self.assertEqual(animation.get_num_frames(), 130)

    def test_gltf_export_indices(self):
        obj = bpy.data.objects['Cube']
        indices = animation.get_gltf_export_indices(obj)
        self.assertEqual(len(indices), 14)

    def test_get_object_actions(self):
        obj = bpy.data.objects['Cube']
        actions = animation.get_object_actions(obj)
        self.assertEqual(len(actions), 0)


