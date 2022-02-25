import bpy
from ..helpers import require_bake_scene, set_scene, set_rendering, set_selection

def bake_all_bake_targets(operator, context, ht):

	bake_scene = require_bake_scene(context)
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
	set_scene(context, bake_scene)

	for bake_target in ht.bake_target_collection:
		for variant in bake_target.variant_collection:
			#TODO - we should take into account bake groups - maybe also move this out to a more generic function
			set_rendering(view_layer.objects, variant.workmesh)
			set_selection(view_layer.objects, variant.workmesh, synchronize_active=True, make_sure_active=True)
			bake_specific_variant(ht, view_layer, bake_target, variant)


def bake_selected_bake_target(operator, context, ht):

	bake_scene = require_bake_scene(context)
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
	set_scene(context, bake_scene)

	if bake_target := ht.get_selected_bake_target():
		if variant := bake_target.variant_collection[bake_target.selected_variant]:
			bake_specific_variant(ht, view_layer, bake_target, variant)

def bake_selected_workmeshes(operator, context, ht):
	# We are currently assuming that we already are in the bake scene

	bake_scene = require_bake_scene(context)
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one

	#NOTE - see technical detail 5 for further info on this temporary solution
	def get_bake_target_and_variant_from_workmesh(workmesh):
		for bake_target in ht.bake_target_collection:
			for variant in bake_target.variant_collection:
				if variant.workmesh == workmesh:
					return bake_target, variant

		raise Exception()	#TODO

	#TODO - make helper function for this
	selection = list()
	for workmesh in view_layer.objects:
		if workmesh.select_get(view_layer=view_layer):
			selection.append(get_bake_target_and_variant_from_workmesh(workmesh))


	for bake_target, variant in selection:
		bake_specific_variant(ht, view_layer, bake_target, variant)



def bake_specific_variant(ht, view_layer, bake_target, variant):
	workmesh = variant.workmesh

	#TODO - we should take into account bake groups - maybe also move this out to a more generic function
	set_rendering(view_layer.objects, workmesh)
	set_selection(view_layer.objects, workmesh, synchronize_active=True, make_sure_active=True)

	# set active image in material
	material_nodes = workmesh.active_material.node_tree.nodes
	material_nodes.active = material_nodes['tex_target']

	# set active UV index to source UV Map (since we want this in the final atlas)
	uv_layers = workmesh.data.uv_layers
	uv_layers.active = uv_layers[bake_target.source_uv_map]

	# here we assume the state is correct for this operation but as discussed in issue #12 we may want to do this in a bit of a different manner which would improve how defined the state is here as well
	bpy.ops.object.bake(type='DIFFUSE')

	#TODO - currently we are not saving the image, we should probably do this after the bulk, though doing it for each part could be good in case there is a problem half way through, something to discuss
