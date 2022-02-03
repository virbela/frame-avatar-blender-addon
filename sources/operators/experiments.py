def experiment_1(operator, context, ht):

	import bpy
	print(bpy.context.active_object)
	return


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
		set_selection(view_layer.objects, target, synchronize_active=True, make_sure_active=True)

		# perform baking
		bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')

		# switch material to preview material
		target.active_material = preview_material
