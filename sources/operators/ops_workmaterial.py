import bpy
from ..constants import MIRROR_TYPE
from ..logging import log_writer as log
from ..materials import setup_bake_material, get_material_variants
from ..helpers import (
	set_scene, 
	set_selection,
	require_bake_scene, 
	require_named_entry, 
	get_bake_target_variant_name
)

def update_all_materials(operator, context, ht):
	for bake_target in ht.bake_target_collection:
		for variant_name, variant in bake_target.iter_variants():
			update_workmesh_materials(context, ht, bake_target, variant)


def update_selected_material(operator, context, ht):
	if bake_target := ht.get_selected_bake_target():
		if variant := bake_target.variant_collection[bake_target.selected_variant]:
			update_workmesh_materials(context, ht, bake_target, variant)


def switch_to_bake_material(operator, context, ht):
	generic_switch_to_material(context, ht, 'bake')


def switch_to_preview_material(operator, context, ht):
	generic_switch_to_material(context, ht, 'preview')


def select_by_atlas(operator, context, ht):

	selection = list()
	for bake_target in ht.bake_target_collection:
		for variant_name, variant in bake_target.iter_variants():
			if variant.intermediate_atlas == ht.select_by_atlas_image:
				selection.append(variant.workmesh)


	bake_scene = require_bake_scene(context)
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
	set_scene(context, bake_scene)
	set_selection(view_layer.objects, *selection, synchronize_active=True, make_sure_active=True)


def update_workmesh_materials(context, ht,  bake_target, variant):
	#TODO - create all materials

	#TBD - should we disconnect the material if we fail to create one? This might be good in order to prevent accidentally getting unintended materials activated
	if not variant.uv_map:
		variant.workmesh.active_material = None
		log.error(f'Missing UV map for {variant}')
		return

	bake_material_name =f'bake-{get_bake_target_variant_name(bake_target, variant)}'
	if bake_material_name in bpy.data.materials:
		# Remove existing
		bpy.data.materials.remove(bpy.data.materials[bake_material_name])
	
	bake_material = bpy.data.materials.new(bake_material_name)
	bake_material.use_nodes = True	#contribution note 9
	#TBD should we use source_uv_map here or should we consider the workmesh to have an intermediate UV map?
	setup_bake_material(bake_material.node_tree, variant.intermediate_atlas, bake_target.source_uv_map, variant.image, variant.uv_map)
	variant.workmesh.active_material = bake_material


def generic_switch_to_material(context, ht, material_type):
	bake_scene = require_bake_scene(context)
	#todo note 1
	for bt in ht.bake_target_collection:
		mirror, mt = bt.get_mirror_type(ht)
		if mt is MIRROR_TYPE.SECONDARY:
			continue

		atlas = bt.atlas
		uv_map = bt.source_uv_map

		if atlas and uv_map:
			variant_materials = get_material_variants(bt, bake_scene, atlas, uv_map)

			for variant_name, variant in bt.iter_bake_scene_variants():
				target = require_named_entry(bake_scene.objects, variant_name)
				materials = variant_materials[variant_name]
				# set active material
				target.active_material = bpy.data.materials[getattr(materials, material_type)]
		else:
			log.warning(f'{bt.name} lacks atlas or uv_map')
