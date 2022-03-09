import bpy
from .common import set_uv_map
from ..logging import log_writer as log
from ..materials import setup_bake_material
from ..helpers import (
	purge_object,
    require_bake_scene, 
    IMPLEMENTATION_PENDING,
    get_bake_target_variant_name,
)

update_selected_workmesh = IMPLEMENTATION_PENDING
update_all_workmeshes = IMPLEMENTATION_PENDING
update_selected_workmesh_all_shapekeys = IMPLEMENTATION_PENDING
update_selected_workmesh_active_shapekey = IMPLEMENTATION_PENDING

def create_workmeshes_for_all_targets(operator, context, ht):
	bake_scene = require_bake_scene(context)
	for bake_target in ht.bake_target_collection:
		create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target)


def create_workmeshes_for_selected_target(operator, context, ht):
	#TODO - handle no selected target
	if bake_target := ht.get_selected_bake_target():
		bake_scene = require_bake_scene(context)
		create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target)


def create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target):
	#TODO - when conditions fail we should add log entries
	for variant in bake_target.variant_collection:

		pending_name = get_bake_target_variant_name(bake_target, variant)

		# if the workmesh was previously created, skip 
		if pending_name in bpy.data.objects:
			# NOTE(ranjian0) since artists may have performed actions on the workmeshs, 
			# we choose to skip regeneration.
			log.warning(f'Skipping existing workmesh ...')
			continue

		if source_object := bake_target.source_object:
			pending_object = source_object.copy()
			pending_object.name = pending_name
			pending_object.data = source_object.data.copy()
			pending_object.data.name = pending_name

			# Create UV map for painting
			bake_uv = pending_object.data.uv_layers[0]	# Assume first UV map is the bake one
			local_uv = pending_object.data.uv_layers.new(name=PAINTING_UV_NAME)
			set_uv_map(pending_object, local_uv.name)

			# check if this target uses a shape key
			if shape_key := pending_object.data.shape_keys.key_blocks.get(bake_target.shape_key_name):
				#Remove all shapekeys except the one this object represents
				for key in pending_object.data.shape_keys.key_blocks:
					if key.name != bake_target.shape_key_name:
						pending_object.shape_key_remove(key)

				#Remove remaining
				for key in pending_object.data.shape_keys.key_blocks:
					pending_object.shape_key_remove(key)

		bake_scene.collection.objects.link(pending_object)

		#TODO - should we create a link from workmesh to the bake target variant? Is this possible? See technical detail 5
		#TODO - we need to document the data structures properly for better planning and overview

		variant.workmesh = pending_object
		variant.uv_map = local_uv.name
		bake_target.uv_map = bake_uv.name		#TODO - should the target be in each variant perhaps?

		update_workmesh_materials(context, ht, bake_target, variant)


def update_workmesh_materials(context, ht,  bake_target, variant):
	#TODO - create all materials

	#TBD - should we disconnect the material if we fail to create one? This might be good in order to prevent accidentally getting unintended materials activated
	if not variant.uv_map:
		variant.workmesh.active_material = None
		print('no uv')
		return

	bake_material_name =f'bake-{get_bake_target_variant_name(bake_target, variant)}'
	bake_material = bpy.data.materials.new(bake_material_name)
	bake_material.use_nodes = True	#contribution note 9
	#TBD should we use source_uv_map here or should we consider the workmesh to have an intermediate UV map?
	setup_bake_material(bake_material.node_tree, variant.intermediate_atlas, bake_target.source_uv_map, variant.image, variant.uv_map)
	variant.workmesh.active_material = bake_material
