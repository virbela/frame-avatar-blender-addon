import bpy
import unittest

from src.utils import helpers

class TestUtilsHelpers(unittest.TestCase):
    def test_implementation_pending(self):
        not_implemented_func = helpers.IMPLEMENTATION_PENDING

        with self.assertRaises(helpers.InternalError):
            not_implemented_func()

    def test_require_scenes(self):
        b_sc = helpers.require_bake_scene(bpy.context)
        m_sc = helpers.require_work_scene(bpy.context)
        self.assertIsNotNone(b_sc)
        self.assertEqual(b_sc.name, "Baking")
        self.assertIsNotNone(m_sc)
        self.assertEqual(m_sc.name, "Scene")
