import bpy
import unittest

from src.utils import helpers
from src.utils import exceptions

class TestUtilsHelpers(unittest.TestCase):
    def test_implementation_pending(self):
        not_implemented_func = helpers.IMPLEMENTATION_PENDING

        with self.assertRaises(helpers.InternalError):
            not_implemented_func()

    def test_require_scenes(self):
        b_sc = helpers.require_bake_scene()
        m_sc = helpers.require_work_scene()
        self.assertIsNotNone(b_sc)
        self.assertEqual(b_sc.name, "Baking")
        self.assertIsNotNone(m_sc)
        self.assertEqual(m_sc.name, "Scene")

    def test_named_entry(self):
        self.assertIsNotNone(helpers.get_named_entry(bpy.data.objects, "Cube"))
        self.assertIsNone(helpers.get_named_entry(bpy.data.objects, "Cubexxx"))

        with self.assertRaises(exceptions.FrameException.NamedEntryNotFound):
            helpers.require_named_entry(bpy.data.objects, "Cubezz")

    def test_get_nice_name(self):
        name = helpers.get_nice_name(bpy.data.objects, "Cube", 10)
        self.assertEqual(name, "Cube-001")

        with self.assertRaises(Exception):
            for _ in range(11):
                name = helpers.get_nice_name(bpy.data.objects, "Cube", 10, max_tries=10)
                bpy.data.objects.new(name, None)

    def test_is_reference_valid(self):
        obj = bpy.data.objects.new("testobj", None)
        self.assertTrue(helpers.is_reference_valid(obj))

        bpy.data.objects.remove(obj)
        self.assertFalse(helpers.is_reference_valid(obj))

    def test_purge_object(self):
        obj = bpy.data.objects.new("testobj1", None)
        helpers.purge_object(obj)

        self.assertIsNone(bpy.data.objects.get("testobj1"))

    def test_ensure_applied_rotation(self):
        obj = bpy.data.objects["Cube"]
        obj.rotation_euler.x = 90

        helpers.ensure_applied_rotation(obj)
        self.assertEqual(tuple(obj.rotation_euler), (0, 0, 0))

