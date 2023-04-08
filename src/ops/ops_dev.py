import bpy
from bpy.types import Operator, Context
from ..utils.helpers import require_bake_scene
from ..utils.properties import HomeomorphicProperties
from ..utils.bone_animation_viewer import view_animation

def clear_bake_targets(operator: Operator, context: Context, ht: HomeomorphicProperties):
	ht.selected_bake_target = -1
	while len(ht.bake_target_collection):
		ht.bake_target_collection.remove(0)

	ht.selected_bake_target_mirror = -1
	while len(ht.bake_target_mirror_collection):
		ht.bake_target_mirror_collection.remove(0)


def clear_bake_scene(operator: Operator, context: Context, ht: HomeomorphicProperties):
	scene = require_bake_scene(context)
	for item in scene.objects:
		if item.type == 'MESH':
			bpy.data.meshes.remove(item.data, do_unlink=True)
		elif item.type == 'ARMATURE':
			bpy.data.armatures.remove(item.data, do_unlink=True)


def debug_bone_animation(operator: Operator, context: Context, ht: HomeomorphicProperties):
	if ht.debug_animation_name:
		ht.debug_animation_show = not ht.debug_animation_show
		view_animation(animation=ht.debug_animation_name, show=ht.debug_animation_show)