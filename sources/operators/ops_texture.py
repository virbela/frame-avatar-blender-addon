import bpy
import bmesh
from .common import set_uv_map, guarded_operator 
from ..structures import intermediate
from ..logging import log_writer as log
from ..helpers import (
    set_scene,
    set_active,
    set_selection,
    clear_selection,
	named_entry_action,
    create_named_entry, 
    require_bake_scene
)

UVPM2_INSTALLED = lambda: "uvpackmaster2" in dir(bpy.ops)

if UVPM2_INSTALLED():
	disable_packing_box = guarded_operator(bpy.ops.uvpackmaster2.disable_target_box)
	enable_packing_box = guarded_operator(bpy.ops.uvpackmaster2.enable_target_box)


def auto_assign_atlas(operator, context, ht):
	'Goes through all bake targets and assigns them to the correct intermediate atlas and UV set based on the uv_mode'

	#TODO - currently we don't take into account that variants may end up on different bins which is fine but we need to store the intermediate target with the variant and not the bake target
	#TODO - currently we will just hardcode the intermediate atlases but later we need to check which to use and create them if needed
	a_width = ht.atlas_size
	a_height = ht.atlas_size

	atlas_color = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_color', 	a_width, a_height, action=named_entry_action.GET_EXISTING)
	atlas_red = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_red', 		a_width, a_height, action=named_entry_action.GET_EXISTING)
	atlas_green = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_green', 	a_width, a_height, action=named_entry_action.GET_EXISTING)
	atlas_blue = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_blue', 	a_width, a_height, action=named_entry_action.GET_EXISTING)


	#TODO - here we need to put things in bins like how the UV packing does below but before we can do this we should look at the variants
	#TBD - should we do it all from beginning? for now yes - maybe later we can have selection

	#TO-DOC - document what happens here properly

	uv_object_list = get_intermediate_uv_object_list(ht)

	monochrome_targets = list()
	color_targets = list()
	nil_targets = list()
	frozen_targets = list()
	for uv in uv_object_list:
		if uv.bake_target.uv_mode == 'UV_IM_MONOCHROME':
			monochrome_targets.append(uv)
		elif uv.bake_target.uv_mode == 'UV_IM_COLOR':
			color_targets.append(uv)
		elif uv.bake_target.uv_mode == 'UV_IM_NIL':
			nil_targets.append(uv)
		elif uv.bake_target.uv_mode == 'UV_IM_FROZEN':
			frozen_targets.append(uv)
		else:
			raise Exception(uv.bake_target.uv_mode)	#TODO proper exception

	log.debug(f'UV bins - monochrome: {len(monochrome_targets)}, color: {len(color_targets)}, nil: {len(nil_targets)}, frozen: {len(frozen_targets)}')


	#NOTE - we support multiple color bins but it is not used yet
	color_bins = [
		intermediate.packing.atlas_bin('color', atlas=atlas_color),
	]

	mono_bins = [
		intermediate.packing.atlas_bin('red', atlas=atlas_red),
		intermediate.packing.atlas_bin('green', atlas=atlas_green),
		intermediate.packing.atlas_bin('blue', atlas=atlas_blue),
	]


	all_targets = [
		(monochrome_targets, mono_bins),
		(color_targets, color_bins),
	]

	for target_list, bin_list in all_targets:
		for uv_island in sorted(target_list, reverse=True, key=lambda island: island.area):
			uv_island.bin = target_bin = min(bin_list, key=lambda bin: bin.allocated)
			uv_island.variant.intermediate_atlas = target_bin.atlas
			target_bin.allocated += uv_island.area


def pack_uv_islands(operator, context, ht):
	last_active_scene = context.scene

	bake_scene = require_bake_scene(context)
	all_uv_object_list = get_intermediate_uv_object_list(ht)
	mono_box = (0.0, 1.0, 1.0, ht.color_percentage / 100.0)
	color_box = (0.0, 0.0, 1.0, ht.color_percentage / 100.0)

	pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_red'], 'UVMap', mono_box)
	pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_green'], 'UVMap', mono_box)
	pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_blue'], 'UVMap', mono_box)
	pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_color'], 'UVMap', color_box)

	set_scene(context, last_active_scene)

def get_intermediate_uv_object_list(ht):
	uv_object_list = list()
	#todo note 1
	for bake_target in ht.bake_target_collection:
		#mirror, mt = bake_target.get_mirror_type(ht)

		if bake_target.bake_mode == 'UV_BM_REGULAR':

			for variant_name, variant in bake_target.iter_variants():
				if not variant.workmesh: 
					continue

				mesh = bmesh.new()
				mesh.from_mesh(variant.workmesh.data)
				uv_area = sum(face.calc_area() * bake_target.uv_area_weight for face in mesh.faces)
				mesh.free()

				uv_object_list.append(intermediate.packing.bake_target(bake_target, variant, uv_area, variant_name))

	return uv_object_list


def pack_intermediate_atlas(context, bake_scene, all_uv_object_list, atlas, uv_map, box=None):
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
	set_scene(context, bake_scene)

	uv_object_list = [u for u in all_uv_object_list if u.variant.intermediate_atlas == atlas]
	if not uv_object_list:
		# XXX nothing todo for this atlas
		return

	for uv_island in uv_object_list:
		scale_factor = uv_island.area * uv_island.bake_target.uv_area_weight
		copy_and_transform_uv(
			uv_island.bake_target.source_object, 
			uv_island.bake_target.source_uv_map, 
			uv_island.variant.workmesh, uv_map, scale_factor
		)

	#TO-FIX skipping partitioning object temporarily
	set_selection(view_layer.objects, *(u.variant.workmesh for u in uv_object_list))
	# set first to active since we need an arbritary active object
	set_active(view_layer.objects, uv_object_list[0].variant.workmesh)

	# enter edit mode and select all faces and UVs
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')	#Select faces in model editor
	bpy.ops.uv.select_all(action='SELECT')		#Select UVs in UV editor

	if UVPM2_INSTALLED():
		bpy.ops.uvpackmaster2.split_overlapping_islands()
		bake_scene.uvp2_props.rot_step = 45

		# note - we use guarded operators for setting the state of the packing box since setting it to the same state it already is will fail
		disable_packing_box()

		if box:
			(	bake_scene.uvp2_props.target_box_p1_x,
				bake_scene.uvp2_props.target_box_p1_y,
				bake_scene.uvp2_props.target_box_p2_x,
				bake_scene.uvp2_props.target_box_p2_y ) = box

			enable_packing_box()


		#NOTE - if we later do downsampling when doing final bake - we must consider the final pixel margin and not the intermediate one!
		bake_scene.uvp2_props.pixel_margin = 5	#TODO - not hardcode! We could just not set this and set it in UVP UI but I think it is better this is a setting in FABA so that we don't forget about it

		bpy.ops.uvpackmaster2.uv_pack()
		disable_packing_box()
	else:
		bpy.ops.uv.average_islands_scale()
		bpy.ops.uv.pack_islands(margin=0.01)

	clear_selection(view_layer.objects)
	bpy.ops.object.mode_set(mode='OBJECT')


def copy_and_transform_uv(source_object, source_layer, target_object, target_layer, scale_factor=1.0):

	#TODO - investigate if we can get uv layer index without actually changing it and getting mesh.loops.layers.uv.active
	bpy.ops.object.mode_set(mode='OBJECT')

	#TODO - would be great if we made a context manager for these commands so that we could reset all changes when exiting the context (this applies to a lot of things outside this function too)
	set_uv_map(source_object, source_layer)
	set_uv_map(target_object, target_layer)

	source_mesh = bmesh.new()
	source_mesh.from_mesh(source_object.data)
	source_uv_layer_index = source_mesh.loops.layers.uv.active

	target_mesh = bmesh.new()
	target_mesh.from_mesh(target_object.data)
	target_uv_layer_index = target_mesh.loops.layers.uv.active

	#TODO - use a strict zip here so we can detect error and also handle any such errors using the .free() methods in the finalization handler
	for source_face, target_face in zip(source_mesh.faces, target_mesh.faces):
		for source_loop, target_loop in zip(source_face.loops, target_face.loops):
			source_uv = source_loop[source_uv_layer_index].uv
			target_loop[target_uv_layer_index].uv = source_uv * scale_factor

	target_mesh.to_mesh(target_object.data)
	source_mesh.free()
	target_mesh.free()
