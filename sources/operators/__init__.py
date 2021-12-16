from .base import frame_operator
from ..logging import log_writer as log
from . import operations


class FRAME_OT_auto_assign_atlas(frame_operator):
	bl_label = 			"Auto assign atlas/UV"
	bl_idname = 		"frame.auto_assign_atlas"
	bl_description = 	"Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
	frame_operator = 	operations.auto_assign_atlas

class FRAME_OT_update_baking_scene(frame_operator):
	bl_label = 			"Update baking scene"
	bl_idname = 		"frame.update_baking_scene"
	#TODO - bl_description
	frame_operator = 	operations.update_bake_scene

class FRAME_OT_pack_uv_islands(frame_operator):
	bl_label = 			"Pack UV islands"
	bl_idname = 		"frame.pack_uv_islands"
	#TODO - bl_description
	frame_operator = 	operations.pack_uv_islands

class FRAME_OT_bake_all(frame_operator):
	bl_label = 			"Bake all bake targets"
	bl_idname = 		"frame.bake_all"
	#TODO - bl_description
	frame_operator = 	operations.bake_all_bake_targets

class FRAME_OT_bake_selected(frame_operator):
	#TODO - if we support multiple targets in selection we should change to plural here
	bl_label = 			"Bake selected bake target"
	bl_idname = 		"frame.bake_selected"
	#TODO - bl_description
	frame_operator = 	operations.bake_selected_bake_targets

class FRAME_OT_create_bake_targets_from_shapekeys(frame_operator):
	bl_label = 			"Create bake targets"
	bl_description = 	'Creates bake targets based on a specific naming convention'
	bl_idname = 		'frame.create_bake_targets_from_shapekeys'
	frame_operator = 	operations.create_bake_targets_from_shapekeys

class FRAME_OT_set_bake_mirror_primary(frame_operator):
	bl_label = 			"Set primary"
	bl_description = 	'Set primary bake target of selected mirror entry'
	bl_idname = 		'frame.set_bake_mirror_primary'
	frame_operator = 	operations.bake_mirrors.set_primary

class FRAME_OT_set_bake_mirror_secondary(frame_operator):
	bl_label = 			"Set secondary"
	bl_description = 	'Set secondary bake target of selected mirror entry'
	bl_idname = 		'frame.set_bake_mirror_secondary'
	frame_operator = 	operations.bake_mirrors.set_secondary

class FRAME_OT_add_bake_target_mirror(frame_operator):
	bl_label = 			"+"
	bl_description = 	'Create new mirror entry'
	bl_idname = 		'frame.add_bake_target_mirror'
	frame_operator = 	operations.bake_mirrors.add

class FRAME_OT_remove_bake_target_mirror(frame_operator):
	bl_label =			"-"
	bl_description = 	'Remove mirror entry'
	bl_idname = 		'frame.remove_bake_target_mirror'
	frame_operator = 	operations.bake_mirrors.remove

class FRAME_OT_add_bake_target(frame_operator):
	bl_label =			"+"
	bl_description = 	'Create new bake target'
	bl_idname = 		'frame.add_bake_target'
	frame_operator = 	operations.bake_targets.add

class FRAME_OT_remove_bake_target(frame_operator):
	bl_label = 			"-"
	bl_description = 	'Remove selected bake target'
	bl_idname = 		'frame.remove_bake_target'
	frame_operator = 	operations.bake_targets.remove

class FRAME_OT_add_bake_target_variant(frame_operator):
	bl_label = 			"+"
	bl_description = 	'Add variant'
	bl_idname = 		'frame.add_bake_target_variant'
	frame_operator =	operations.bake_variants.add

class FRAME_OT_remove_bake_target_variant(frame_operator):
	bl_label =			"-"
	bl_description = 	'Remove mirror entry'
	bl_idname = 		'frame.remove_bake_target_variant'
	frame_operator = 	operations.bake_variants.remove


#DEPRECHATED ↓↓↓

import random, string
def gen_random_hash(length):
	return ''.join(random.choice(string.hexdigits) for i in range(length))

def get_unique_name(collection, prefix, max_prefix_length, random_hash_length=8, max_tries=1024):
	for v in range(max_tries):
		candidate = f'{prefix[:max_prefix_length]}-{gen_random_hash(random_hash_length)}'
		if candidate not in collection:
			return candidate

	raise Exception('severe fail')	#TODO - proper exception

#DEPRECHATED ↑↑↑


def get_nice_name(collection, prefix, max_prefix_length, random_hash_length=8, max_tries=1000):

	for v in range(max_tries):
		tail = f'-{v:03}' if v else ''
		candidate = f'{prefix[:max_prefix_length]}{tail}'
		if candidate not in collection:
			return candidate

	raise Exception('severe fail')	#TODO - proper exception


#TODO - remove this one for distribution
#NOTICE - we currently don't have a reasonable way of quickly including or excluding aspects since python doesn't have a preprocessor. We can solve this somehow later though but currently manual intervention is required
#	One solution would be to use a variable in a module but the minor drawback is that the code would still be there, even though it would not be run (this is probably a good solution)


#BUG - we have to make sure we have the correct UV layer active for rendering - there is a distinction
#		both the selected and render-active plays role in the UV Maps list box - need to figure out how this works and how it relates
#		to the active node in the node editor - perhaps that was a red herring
#BUG - when we pack UVs we also scale the wrong UV layer - we need to limit this to the right layer

class FRAME_OT_experiments(frame_operator):
	bl_label = 			"Placeholder for experiments"
	bl_idname = 		"frame.place_holder_for_experiments"
	bl_description =	"This is for internal development purposes and should not be seen in distribution"
	def frame_operator(operator, context, ht):
		bt = ht.get_selected_bake_target()

		if not bt:
			return

		from .. import materials
		from ..helpers import create_named_entry, set_selection, set_active, get_bake_scene, require_named_entry
		import bpy
		from ..constants import MIRROR_TYPE


		mirror, mt = bt.get_mirror_type(ht)


		if mt is MIRROR_TYPE.PRIMARY:
			log.debug(f'{bt.name} is primary of mirror {mirror}, so we should bake it')
		elif mt is MIRROR_TYPE.SECONDARY:
			log.debug(f'{bt.name} is secondary of mirror {mirror}, so we should NOT bake it')
			return
		else:
			log.debug(f'{bt.name} is not a mirror, so we should bake it')

		atlas = bt.require_atlas()
		uv_map = bt.uv_set



		bake_scene = get_bake_scene(context)
		context.window.scene = bake_scene
		view_layer = bake_scene.view_layers[0]	#TODO - should make sure there is only one

		#NOTE - one way to create the materials in a reasonable fascion is to name them according to the settings that can be different
		#		currently a material is defined by 4 properties - target atlas, target uv, [diffuse atlas, diffuse uv] - where [] denotes optional
		#	    One really useful property of creating all the materials other than potential caching benefits within blender is to be able
		#		to troubleshoot baking by inspecting materials.

		# The final solution should prepare all materials before executing batch baking
		# but in this test we will do it here


		# Setup materials here
		#TODO - we should handle the case of not using variants
		#NOTE - Here we create the materials
		variant_material_cache = dict()	#NOTE - this cache should not reside here of course but we use it in this test - it should be in a module but should not be a saved state.
		for variant_name, variant in bt.iter_bake_scene_variants():
			target = require_named_entry(bake_scene.objects, variant_name)

			if variant.image:
				paint_image = bpy.data.images[variant.image]	#TODO - make sure this image exists
				paint_uv = 'Diffuse'
				#TBD - could this yield way too long names? Should we use a "{shortname}-{shorthash}" naming scheme?

				#NOTE - we are hitting the 63 char limit here! - we will use hash variant
				# 		pattern here was f'bake.{variant_name}.{atlas.name}.{uv_map}.{paint_image.name}.{paint_uv}'

				material_name = get_nice_name(variant_material_cache, f'bake-{bt.shortname}-{variant.name}', 32)

				#NOTE - we were not going to recreate materials but in this test we are doing the materials setup which SHOULD recreate them in case something was changed
				bake_baterial = create_named_entry(bpy.data.materials, material_name, recreate=True)
				bake_baterial.use_nodes = True	#contribution note 9

				#TODO - this is just for testing!!
				#TODO - make sure we even have a variant since not all targets have those
				materials.setup_bake_material2(bake_baterial.node_tree, atlas, uv_map, paint_image, paint_uv)
			else:
				raise Exception('not implemented')	#TODO - implement

			#store what material we are using
			variant_material_cache[variant_name] = material_name


		# Do baking here
		for variant_name, variant in bt.iter_bake_scene_variants():
			target = require_named_entry(bake_scene.objects, variant_name)

			bake_baterial = bpy.data.materials[variant_material_cache[variant_name]]

			target.active_material = bake_baterial
			view_layer.objects.active = target
			set_selection(view_layer.objects, target)
			set_active(view_layer.objects, target)
			overrides = dict(
				scene = bake_scene
			)
			bpy.ops.object.bake(overrides, type='DIFFUSE', save_mode='EXTERNAL')


#TODO - this should be guarded by a devmode boolean
class FRAME_OT_node_get_links(frame_operator):
	bl_label = 			"Copy links"
	bl_idname = 		"frame.create_node_script"
	bl_description =	"Enumerate links to stdout for programmtic replication"

	frame_operator = operations.devtools.get_node_links

