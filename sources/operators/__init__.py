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



#TODO - remove this one for distribution
#NOTICE - we currently don't have a reasonable way of quickly including or excluding aspects since python doesn't have a preprocessor. We can solve this somehow later though but currently manual intervention is required
#	One solution would be to use a variable in a module but the minor drawback is that the code would still be there, even though it would not be run (this is probably a good solution)
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
		make_baterial = create_named_entry(bpy.data.materials, 'testmat', recreate=True)
		make_baterial.use_nodes = True	#contribution note 9

		#TODO - this is just for testing!!
		paint_image = bpy.data.images['eye_texture.png']

		materials.setup_bake_material2(make_baterial.node_tree, atlas, uv_map, paint_image)

		bake_scene = get_bake_scene(context)
		context.window.scene = bake_scene
		view_layer = bake_scene.view_layers[0]	#TODO - should make sure there is only one

		for variant in bt.iter_bake_scene_variant_names():
			target = require_named_entry(bake_scene.objects, variant)

			target.active_material = make_baterial
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

