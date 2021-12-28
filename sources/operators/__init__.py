from .base import frame_operator
from ..logging import log_writer as log
from . import operations


class FRAME_OT_new_workmesh_from_selected(frame_operator):
	bl_label = 			"New from selected"
	bl_idname = 		"frame.new_workmesh_from_selected"
	#TODO - bl_description
	frame_operator = 	operations.new_workmesh_from_selected

class FRAME_OT_update_selected_workmesh_all_shapekeys(frame_operator):
	bl_label = 			"Update selected"
	bl_idname = 		"frame.update_selected_workmesh_all_shapekeys"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_workmesh_all_shapekeys

class FRAME_OT_update_selected_workmesh_active_shapekey(frame_operator):
	bl_label = 			"Update active shapekey"
	bl_idname = 		"frame.update_selected_workmesh_active_shapekey"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_workmesh_active_shapekey


class FRAME_OT_setup_bake_scene(frame_operator):
	bl_label = 			"First time setup"
	bl_idname = 		"frame.setup_bake_scene"
	bl_description = 	"Create bake scene"
	frame_operator = 	operations.setup_bake_scene


class FRAME_OT_validate_targets(frame_operator):
	bl_label = 			"Validate bake targets"
	bl_idname = 		"frame.validate_targets"
	#TODO - bl_description
	frame_operator = 	operations.validate_targets

class FRAME_OT_update_selected_workmesh(frame_operator):
	bl_label = 			"Update selected work mesh"
	bl_idname = 		"frame.update_selected_workmesh"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_workmesh

class FRAME_OT_update_all_workmeshes(frame_operator):
	bl_label = 			"Update all work meshes"
	bl_idname = 		"frame.update_all_workmeshes"
	#TODO - bl_description
	frame_operator = 	operations.update_all_workmeshes

class FRAME_OT_update_selected_material(frame_operator):
	bl_label = 			"Update selected material"
	bl_idname = 		"frame.update_selected_material"
	#TODO - bl_description
	frame_operator = 	operations.update_selected_material

class FRAME_OT_update_all_materials(frame_operator):
	bl_label = 			"Update all materials"
	bl_idname = 		"frame.update_all_materials"
	#TODO - bl_description
	frame_operator = 	operations.update_all_materials

class FRAME_OT_auto_assign_atlas(frame_operator):
	bl_label = 			"Auto assign atlas/UV"
	bl_idname = 		"frame.auto_assign_atlas"
	bl_description = 	"Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
	frame_operator = 	operations.auto_assign_atlas

#TBD - should we have this one?
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

class FRAME_OT_show_selected_bt(frame_operator):
	bl_label =			"Edit selected"
	bl_description = 	(
							'Edit selected bake target.\n'
							'Activates shape key is needed'
						)
	bl_idname = 		'frame.show_selected_bt'
	frame_operator = 	operations.bake_targets.edit_selected

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

class FRAME_OT_switch_to_bake_material(frame_operator):
	bl_label =			"Show bake/paint material"
	bl_description = 	'Switch all bake objects to use the bake material'
	bl_idname = 		'frame.switch_to_bake_material'
	frame_operator = 	operations.switch_to_bake_material

class FRAME_OT_switch_to_preview_material(frame_operator):
	bl_label =			"Show preview material"
	bl_description = 	'Switch all bake objects to use the preview material'
	bl_idname = 		'frame.switch_to_preview_material'
	frame_operator = 	operations.switch_to_preview_material

class FRAME_OT_synchronize_mirrors(frame_operator):
	bl_label =			"Synchronize mirrors"
	bl_description = 	'Copy settings from all primary targets to secondary targets in the mirror list'
	bl_idname = 		'frame.synchronize_mirrors'
	frame_operator = 	operations.synchronize_mirrors




from ..materials import get_material_variants



#NOTICE - we currently don't have a reasonable way of quickly including or excluding aspects since python doesn't have a preprocessor. We can solve this somehow later though but currently manual intervention is required
#	One solution would be to use a variable in a module but the minor drawback is that the code would still be there, even though it would not be run (this is probably a good solution)

#TODO - remove this one for distribution
class FRAME_OT_experiments(frame_operator):
	bl_label = 			"Placeholder for experiments"
	bl_idname = 		"frame.place_holder_for_experiments"
	bl_description =	"This is for internal development purposes and should not be seen in distribution"
	def frame_operator(operator, context, ht):
		bt = ht.get_selected_bake_target()

		if not bt:
			return

		from .. import materials
		from ..helpers import create_named_entry, set_selection, set_active, get_bake_scene, require_named_entry, set_scene
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
		uv_map = bt.uv_map



		bake_scene = get_bake_scene(context)
		# switch to bake scene
		set_scene(context, bake_scene)

		view_layer = bake_scene.view_layers[0]	#TODO - should make sure there is only one

		#NOTE - one way to create the materials in a reasonable fascion is to name them according to the settings that can be different
		#		currently a material is defined by 4 properties - target atlas, target uv, [diffuse atlas, diffuse uv] - where [] denotes optional
		#	    One really useful property of creating all the materials other than potential caching benefits within blender is to be able
		#		to troubleshoot baking by inspecting materials.

		# The final solution should prepare all materials before executing batch baking
		# but in this test we will do it here

		#NOTE - we were not going to recreate materials but in this test we are doing the materials setup which SHOULD recreate them in case something was changed
		variant_materials = get_material_variants(bt, bake_scene, atlas, uv_map, recreate=True)

		# Do baking here
		for variant_name, variant in bt.iter_bake_scene_variants():
			target = require_named_entry(bake_scene.objects, variant_name)
			materials = variant_materials[variant_name]
			bake_material = bpy.data.materials[materials.bake]
			preview_material = bpy.data.materials[materials.preview]

			# select bake material as active material
			target.active_material = bake_material
			# set active view layer object and selection
			#TODO - check how to do this for a bake group
			set_selection(view_layer.objects, target)
			set_active(view_layer.objects, target)

			# perform baking
			bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')

			# switch material to preview material
			target.active_material = preview_material


#TODO - this should be guarded by a devmode boolean
class FRAME_OT_node_get_links(frame_operator):
	bl_label = 			"Copy links"
	bl_idname = 		"frame.create_node_script"
	bl_description =	"Enumerate links to stdout for programmtic replication"

	frame_operator = operations.devtools.get_node_links

