from ..helpers import IMPLEMENTATION_PENDING, get_bake_scene, get_work_scene, a_get, a_set, set_scene, set_selection, set_active, clear_selection, require_named_entry, get_nice_name, create_named_entry
from ..logging import log_writer as log
from ..structures import intermediate, iter_dc
from ..materials import get_material_variants, setup_bake_material
from ..constants import MIRROR_TYPE
from ..bake_targets import validate_all
from .. import constants
import bpy, bmesh
import textwrap


#TODO - fix this!
update_selected_workmesh = IMPLEMENTATION_PENDING
update_all_workmeshes = IMPLEMENTATION_PENDING
update_all_materials = IMPLEMENTATION_PENDING

update_selected_workmesh_all_shapekeys = IMPLEMENTATION_PENDING
update_selected_workmesh_active_shapekey = IMPLEMENTATION_PENDING


def select_by_atlas(operator, context, ht):

	selection = list()
	for bake_target in ht.bake_target_collection:
		for variant_name, variant in bake_target.iter_variants():
			if variant.intermediate_atlas == ht.select_by_atlas_image:
				selection.append(variant.workmesh)


	bake_scene = get_bake_scene(context)
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
	set_scene(context, bake_scene)

	set_selection(view_layer.objects, *selection)




def validate_targets(operator, context, ht):
	validate_all(ht)


def create_mirror(ht, primary, secondary):
	new = ht.bake_target_mirror_collection.add()
	new.primary = primary
	new.secondary = secondary
	return new



def create_targets_from_selection(operator, context, ht):
	bake_scene = get_bake_scene(context)
	for source_object in context.selected_objects:
		if shape_keys := source_object.data.shape_keys:
			create_baketarget_from_key_blocks(ht, source_object, shape_keys.key_blocks, bake_scene)

		else:
			create_baketarget_from_key_blocks(ht, source_object, None, bake_scene)


def update_selected_material(operator, context, ht):

	if bake_target := ht.get_selected_bake_target():
		if variant := bake_target.variant_collection[bake_target.selected_variant]:
			update_workmesh_materials(context, ht, bake_target, variant)

def create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target):
	#TODO - when conditions fail we should add log entries
	for variant in bake_target.variant_collection:

		pending_name = f'{bake_target.name}_{variant.name}'

		if source_object := bake_target.source_object:
			pending_object = source_object.copy()
			pending_object.name = pending_name
			pending_object.data = source_object.data.copy()
			pending_object.data.name = pending_name

			# Create UV map for painting
			bake_uv = pending_object.data.uv_layers[0]	# Assume first UV map is the bake one
			local_uv = pending_object.data.uv_layers.new(name='Painting')	#TODO - not hardcode
			set_uv_map(pending_object, local_uv.name)

			#TBD - what should we do when an object already exists? Remove existing?
			# if bake_target.name != pending_object.name:
			# 	log.warning(f'Name was changed to {pending_object.name}')

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

		variant.workmesh = pending_object
		variant.uv_map = local_uv.name
		bake_target.uv_map = bake_uv.name		#TODO - should the target be in each variant perhaps?

		update_workmesh_materials(context, ht, bake_target, variant)

def create_workmeshes_for_all_targets(operator, context, ht):
	bake_scene = get_bake_scene(context)
	for bake_target in ht.bake_target_collection:
		create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target)

def create_workmeshes_for_selected_target(operator, context, ht):

	#TODO - handle no selected target
	if bake_target := ht.get_selected_bake_target():
		bake_scene = get_bake_scene(context)
		create_workmeshes_for_specific_target(context, ht, bake_scene, bake_target)


def update_workmesh_materials(context, ht,  bake_target, variant):
	#TODO - create all materials

	#TBD - should we disconnect the material if we fail to create one? This might be good in order to prevent accidentally getting unintended materials activated
	if not variant.uv_map:
		variant.workmesh.active_material = None
		print('no uv')
		return

	bake_material_name =f'bake-{bake_target.shortname}-{variant.name}'
	bake_material = bpy.data.materials.new(bake_material_name)
	bake_material.use_nodes = True	#contribution note 9
	setup_bake_material(bake_material.node_tree, bake_target.atlas, bake_target.uv_map, variant.image, variant.uv_map)
	variant.workmesh.active_material = bake_material




def create_baketarget_from_key_blocks(ht, source_object, key_blocks, bake_scene):
	#Create all intermediate targets
	targets = dict()
	mirror_list = list()

	if key_blocks is None:
		targets[None] = intermediate.pending.bake_target(
			name = source_object.name,
			object_name = source_object.name,
			source_object = source_object,
			bake_target = source_object,
			shape_key_name = None,
			uv_mode = 'UV_IM_MONOCHROME',
		)

	else:
		for sk in key_blocks:
			key = sk.name
			targets[key] = intermediate.pending.bake_target(
				name = f'{source_object.name}_{key}',
				object_name = source_object.name,
				source_object = source_object,
				bake_target = source_object,
				shape_key_name = key,
				uv_mode = 'UV_IM_MONOCHROME',
			)



	#Configure targets and mirrors
	for key, target in targets.items():
		if key.endswith('_L'):
			base = key[:-2]
			Rk = f'{base}_R'
			R = targets.get(Rk)

			if R:
				mirror_list.append(intermediate.mirror(target, R))

			else:
				log.error(f"Could not create mirror for {key} since there was no such object `{Rk}´")

		elif key.endswith('_R'):
			pass

		elif key.endswith('__None'):
			target.uv_mode = 'UV_IM_NIL'


	#Create bake targets
	for target in targets.values():
		new = ht.bake_target_collection.add()
		new.variant_collection.add()	# add default variant
		for key, value in iter_dc(target):
			setattr(new, key, value)

		target.bake_target = new


#DEPRECHATED
def create_workmesh_from_key_blocks(ht, source_object, key_blocks, bake_scene):
	#TODO - Here we should run our rules for the naming scheme
	#One of these would be numbers after to indicate grouping

	#Create all intermediate targets
	targets = dict()
	mirror_list = list()

	if key_blocks is None:
		targets[None] = intermediate.pending.bake_target(
			name = source_object.name,
			object_name = source_object.name,
			bake_target = source_object,
			shape_key_name = None,
			uv_mode = 'UV_IM_MONOCHROME',
		)

	else:
		for sk in key_blocks:
			key = sk.name
			targets[key] = intermediate.pending.bake_target(
				name = f'{source_object.name}_{key}',
				object_name = source_object.name,
				bake_target = source_object,
				shape_key_name = key,
				uv_mode = 'UV_IM_MONOCHROME',
			)


	#Configure targets and mirrors
	for key, target in targets.items():
		if key.endswith('_L'):
			base = key[:-2]
			Rk = f'{base}_R'
			R = targets.get(Rk)

			if R:
				mirror_list.append(intermediate.mirror(target, R))

			else:
				log.error(f"Could not create mirror for {key} since there was no such object `{Rk}´")

		elif key.endswith('_R'):
			pass

		elif key.endswith('__None'):
			target.uv_mode = 'UV_IM_NIL'


	#Create corresponding work meshes
	for key, target in targets.items():

		copy_obj = source_object.copy()
		copy_obj.name = target.name
		copy_obj.data = source_object.data.copy()
		copy_obj.data.name = target.name

		#TBD - what should we do when an object already exists? Remove existing?
		if target.name != copy_obj.name:
			log.warning(f'Name was changed to {copy_obj.name}')
			target.name = copy_obj.name

		# check if this target uses a shape key
		if key is not None:
			#Remove all shapekeys except the one this object represents
			for key in copy_obj.data.shape_keys.key_blocks:
				if key.name != target.shape_key_name:
					copy_obj.shape_key_remove(key)

			#Remove remaining
			for key in copy_obj.data.shape_keys.key_blocks:
				copy_obj.shape_key_remove(key)

		#TBD - should we set up a material here for copy_obj?
		#TBD - should we put things in collections based on their source object? Such as all Avatar-objects in one collection
		if target.bake_target.multi_variants:
			for index, variant in enumerate(target.bake_target.variant_collection):
				print('VAR', index, variant)

		else:
			bake_scene.collection.objects.link(copy_obj)

		print(target)

		#TODO - store this target in the addon list


	# #NOTE - there is a bug where we can only set uv_mode (or any other enum) once from the same context.
	# #		To avoid this bug we first create dicts that represents the new bake targets and then we instanciate them below
	# for target in targets.values():
	# 	new = ht.bake_target_collection.add()
	# 	for key, value in iter_dc(target):
	# 		setattr(new, key, value)

	# 	target.bake_target = new

	# #Create mirrors
	# for mirror in mirror_list:
	# 	create_mirror(mirror.primary.bake_target.identifier, mirror.secondary.bake_target.identifier)



def new_workmesh_from_selected(operator, context, ht):

	#TODO - make sure we are in the right scene or inform the user

	for source_object in context.selected_objects:
		if shape_keys := source_object.data.shape_keys:
			create_workmesh_from_key_blocks(ht, source_object, shape_keys.key_blocks, get_bake_scene(context))

		else:
			create_workmesh_from_key_blocks(ht, source_object, None, get_bake_scene(context))





def setup_bake_scene(operator, context, ht):
	get_bake_scene(context)

#TODO - implement proper version of commented-out code blocks in this module
#MINOR-TODO - We could still improve list handling but for the moment it is good enough to strike a balance between maintainability and development

class generic_list:
	'This is an abstract handler for list operations. The operations needs a collection and callables to get and set the current selection'

	@staticmethod
	def add(collection, get_selected, set_selected):
		new = collection.add()
		last_id = len(collection) - 1
		set_selected(last_id)
		return new

	@staticmethod
	def remove(collection, get_selected, set_selected):
		collection.remove(get_selected())
		last_id = len(collection) - 1
		if last_id == -1:
			set_selected(-1)
		else:
			set_selected(min(get_selected(), last_id))


def get_intermediate_uv_object_list(ht):
	uv_object_list = list()
	#todo note 1
	for bake_target in ht.bake_target_collection:
		#mirror, mt = bake_target.get_mirror_type(ht)

		if bake_target.bake_mode == 'UV_BM_REGULAR':

			for variant_name, variant in bake_target.iter_variants():

				mesh = bmesh.new()
				mesh.from_mesh(variant.workmesh.data)
				uv_area = sum(face.calc_area() * bake_target.uv_area_weight for face in mesh.faces)
				mesh.free()

				uv_object_list.append(intermediate.packing.bake_target(bake_target, variant, uv_area, variant_name))

	return uv_object_list




def auto_assign_atlas(operator, context, ht):
	'Goes through all bake targets and assigns them to the correct intermediate atlas and UV set based on the uv_mode'

	#TODO - currently we don't take into account that variants may end up on different bins which is fine but we need to store the intermediate target with the variant and not the bake target

	#TODO - currently we will just hardcode the intermediate atlases but later we need to check which to use and create them if needed
	a_width = 4096
	a_height = 4096

	atlas_color = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_color', 	a_width, a_height, recreate=False, ignore_existing=True)
	atlas_red = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_red', 		a_width, a_height, recreate=False, ignore_existing=True)
	atlas_green = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_green', 	a_width, a_height, recreate=False, ignore_existing=True)
	atlas_blue = 	create_named_entry(	bpy.data.images, 'atlas_intermediate_blue', 	a_width, a_height, recreate=False, ignore_existing=True)


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





	# for bake_target in ht.bake_target_collection:
	# 	if bake_target.bake_mode == 'UV_BM_REGULAR':

	# 		if bake_target.uv_mode == 'UV_IM_MONOCHROME':
	# 			pass	#TODO - implement
	# 		elif bake_target.uv_mode == 'UV_IM_COLOR':
	# 			pass	#TODO - implement
	# 		elif bake_target.uv_mode == 'UV_IM_NIL':
	# 			pass	#TODO - implement
	# 		elif bake_target.uv_mode == 'UV_IM_FROZEN':
	# 			pass	#TODO - implement
	# 		else:
	# 			raise Exception()	#TODO internal error

			# # check uv target channel
			# if bake_target.uv_target_channel == 'UV_TARGET_NIL':
			# 	pass	#TODO - implement
			# elif bake_target.uv_target_channel == 'UV_TARGET_COLOR':
			# 	pass	#TODO - implement
			# elif bake_target.uv_target_channel == 'UV_TARGET_R':
			# 	pass	#TODO - implement
			# elif bake_target.uv_target_channel == 'UV_TARGET_G':
			# 	pass	#TODO - implement
			# elif bake_target.uv_target_channel == 'UV_TARGET_B':
			# 	pass	#TODO - implement
			# else:
			# 	raise Exception()	#TODO internal error





def get_partitioning_object(scene):
	'Gets the partitioning object used in UV packing. If no such object exists, we create it. This will be using the current context so take care when calling this!'
	if existing := scene.objects.get(constants.PARTITIONING_OBJECT):
		return existing

	known_before = set(scene.objects.keys())
	bpy.ops.mesh.primitive_plane_add()
	known_now = set(scene.objects.keys())

	new_objects = known_now - known_before

	assert len(new_objects) == 1	#TODO proper exception

	new_name, = new_objects	# Unpack
	new = scene.objects[new_name]

	new.name = constants.PARTITIONING_OBJECT
	new.hide_render = True
	return new

def set_uv_selection(obj, state):
	mesh = bmesh.from_edit_mesh(obj.data)
	uv_layer_index = mesh.loops.layers.uv.active
	for face in mesh.faces:
		for loop in face.loops:
			uv = loop[uv_layer_index]
			uv.select = state
	mesh.free()


def set_uv_map(obj, uv_map):
	obj.data.uv_layers[uv_map].active = True



def set_face_selection(obj, state):
	#It is important to destroy the bmesh object after adjusting selection but since it is local it will automatically be destroyed at return
	mesh = bmesh.from_edit_mesh(obj.data)
	for face in mesh.faces:
		face.select = state

def assign_uv_coords(obj, assign_coords):
	icoords = iter(assign_coords)
	mesh = bmesh.from_edit_mesh(obj.data)
	uv_layer_index = mesh.loops.layers.uv.active
	for face in mesh.faces:
		for loop, c in zip(face.loops, icoords):
			loop[uv_layer_index].uv = c



bake_all_bake_targets = IMPLEMENTATION_PENDING
bake_selected_bake_targets = IMPLEMENTATION_PENDING


class guarded_operator:
	def __init__(self, operator):
		self.operator = operator

	def __repr__(self):
		return f'<{self.__class__.__name__} of {self.operator}>'

	def __call__(self, *pos, **named):
		if self.operator.poll():
			return self.operator(*pos, **named)


disable_packing_box = guarded_operator(bpy.ops.uvpackmaster2.disable_target_box)
enable_packing_box = guarded_operator(bpy.ops.uvpackmaster2.enable_target_box)


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

#DEPRECATED
def rescale_uv(object, uv_layer, factor):
	bpy.ops.object.mode_set(mode='OBJECT')
	set_uv_map(object, uv_layer)

	mesh = bmesh.new()
	mesh.from_mesh(object.data)

	uv_layer_index = mesh.loops.layers.uv.active

	for face in mesh.faces:
		for loop in face.loops:
			loop[uv_layer_index].uv *= factor

	mesh.to_mesh(object.data)
	mesh.free()


def reset_uv_transformations(bake_targets):
	for bake_target in bake_targets:
		for variant_name, variant in bake_target.iter_variants():
			copy_and_transform_uv(bake_target.source_object, bake_target.source_uv_map, variant.workmesh, variant.uv_map)


def pack_intermediate_atlas(context, bake_scene, all_uv_object_list, atlas, uv_map, box=None):
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
	set_scene(context, bake_scene)

	uv_object_list = [u for u in all_uv_object_list if u.variant.intermediate_atlas == atlas]

	for uv_island in uv_object_list:
		scale_factor = uv_island.area * uv_island.bake_target.uv_area_weight
		copy_and_transform_uv(uv_island.bake_target.source_object, uv_island.bake_target.source_uv_map, uv_island.variant.workmesh, uv_map, scale_factor)

	#TO-FIX skipping partitioning object temporarily
	set_selection(view_layer.objects, *(u.variant.workmesh for u in uv_object_list))
	# set first to active since we need an arbritary active object
	set_active(view_layer.objects, uv_object_list[0].variant.workmesh)

	# enter edit mode and select all faces and UVs
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')	#Select faces in model editor
	bpy.ops.uv.select_all(action='SELECT')		#Select UVs in UV editor


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

	bpy.ops.uvpackmaster2.uv_pack()
	disable_packing_box()

	clear_selection(view_layer.objects)
	bpy.ops.object.mode_set(mode='OBJECT')




def pack_uv_islands(operator, context, ht):

	bake_scene = get_bake_scene(context)
	all_uv_object_list = get_intermediate_uv_object_list(ht)
	mono_box = (0.0, 1.0, 1.0, ht.color_percentage / 100.0)
	color_box = (0.0, 0.0, 1.0, ht.color_percentage / 100.0)

	pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_red'], 'UVMap', mono_box)
	#pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_green'], 'UVMap', mono_box)
	#pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_blue'], 'UVMap', mono_box)
	#pack_intermediate_atlas(context, bake_scene, all_uv_object_list, bpy.data.images['atlas_intermediate_color'], 'UVMap', color_box)



#DEPRECATED
def old_pack_uv_islands(operator, context, ht):

	#TO-DOC these operations should be more clearly documented!

	#PENDING
		# when actually packing
		#		bpy.ops.uvpackmaster2.split_overlapping_islands()

		# calculate margins

	bake_scene = get_bake_scene(context)

	# First we get a list of all the islands
	uv_object_list = list()
	#todo note 1
	for bake_target in ht.bake_target_collection:
		mirror, mt = bake_target.get_mirror_type(ht)
		if mt is MIRROR_TYPE.SECONDARY:
			continue

		elif bake_target.multi_variants:
			for variant_name, variant in bake_target.iter_bake_scene_variants():

				if bake_object := bake_scene.objects.get(variant_name):	#TODO - we need to define a set of variant meshes
					uv_object_list.append(intermediate.packing.bake_target(bake_target, bake_object, variant_name=variant_name))
				else:
					log.warning(f'No bake object found for {bake_target}')

		else:
			if bake_object := bake_target.object_reference:
				uv_object_list.append(intermediate.packing.bake_target(bake_target, bake_object, variant_name=None))

	# In order to work with the UVs we need to create a selection and enter edit mode, see: tech-note 2
	view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
	set_scene(context, bake_scene)

	# Get/create paritioning object
	partitioning_object = get_partitioning_object(bake_scene)

	set_selection(view_layer.objects, partitioning_object, *(u.bake_object for u in uv_object_list))
	# set first to active since we need an arbritary active object
	set_active(view_layer.objects, uv_object_list[0].bake_object)

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')	#Select faces in model editor
	bpy.ops.uv.select_all(action='SELECT')		#Select UVs in UV editor

	# unselect partitioning face
	set_face_selection(partitioning_object, False)

	# makes sure we have the correct UV layer active - see tech-note 3
	for uv in uv_object_list:
		print(uv)
		uv.bake_object.data.uv_layers.active = uv.bake_object.data.uv_layers.get(uv.bake_target.uv_map)

	bpy.ops.uv.average_islands_scale()	#TODO - conditional

	# Now the islands have been rescaled and we will calculate their areas and store it in our intermediate structure
	for uv in uv_object_list:

		uv_map = uv.bake_object.data.uv_layers.get(uv.bake_target.uv_map)

		mesh = bmesh.from_edit_mesh(uv.bake_object.data)
		uv.area = sum(face.calc_area() for face in mesh.faces)
		log.debug(f'PACK	{uv.bake_target.name}	{uv_map} (size: {uv.area} u²)')


	# Now these islands should be distributed to our target packing areas

	# We start by putting them in various bins based on their UV mode
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


	#TODO - if ht.color_percentage is 0 or 100, maybe special cases
	height_fraction = ht.color_percentage / 100.0

	def create_color_blocker():
		assign_uv_coords(partitioning_object, (
			(0.0, 0.0),
			(1.0, 0.0),
			(1.0, height_fraction),
			(0.0, height_fraction),
		))

	def create_monochromatic_blocker():
		assign_uv_coords(partitioning_object, (
			(0.0, height_fraction),
			(1.0, height_fraction),
			(1.0, 1.0),
			(0.0, 1.0),
		))



	already_placed = list()
	# TODO - handle nil targets		- these should be done first so their location is defined and added to already-placed list - they should be in a particular reserved always white part #TBD
	# TODO - handle frozen targets	- these should just be added to the already-placed list so we can pack around them


	# TODO - handle color targets

	# The way pack_to_others work is that it only packs the selected UV islands and avoids unselected ones.
	# This probably means we need to make sure our atlas is not used in places it is not supposed to be
	create_monochromatic_blocker()
	bake_scene.uvp2_props.pack_to_others = True
	bpy.ops.object.mode_set(mode='OBJECT')

	set_selection(view_layer.objects, partitioning_object, *(u.bake_object for u in color_targets))
	# set first to active since we need an arbritary active object
	set_active(view_layer.objects, color_targets[0].bake_object)

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')	#Select faces in model editor
	bpy.ops.uv.select_all(action='SELECT')		#Select UVs in UV editor

	#Select correct UV map for targets
	for target in color_targets:
		set_uv_map(target.bake_object, target.bake_target.uv_map)

	# deselect the blocker
	set_uv_selection(partitioning_object, False)

	# Perform packing
	bpy.ops.uvpackmaster2.uv_pack()

	# TODO - assign proper atlas and uv-map
	# EXPERIMENT
	# for target in color_targets:
	# 	target.bake_target.atlas = 'tinytest'




	# TODO - handle monochrome targets
	create_color_blocker()
	bake_scene.uvp2_props.pack_to_others = True
	bpy.ops.object.mode_set(mode='OBJECT')


	set_selection(view_layer.objects, partitioning_object, *(u.bake_object for u in monochrome_targets))
	# set first to active since we need an arbritary active object
	set_active(view_layer.objects, monochrome_targets[0].bake_object)

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')	#Select faces in model editor
	bpy.ops.uv.select_all(action='SELECT')		#Select UVs in UV editor

	#Select correct UV map for targets
	for target in color_targets:
		set_uv_map(target.bake_object, target.bake_target.uv_map)


	# deselect the blocker
	set_uv_selection(partitioning_object, False)

	# Perform packing
	bpy.ops.uvpackmaster2.uv_pack()




	bpy.ops.object.mode_set(mode='OBJECT')
	clear_selection(view_layer.objects)



def copy_object(source_obj, name):
	new_object = source_obj.copy()
	new_object.data = source_obj.data.copy()	#Copy data as well
	new_object.name = name
	return new_object

def update_bake_scene(operator, context, ht):
	work_scene, bake_scene = get_work_scene(context), get_bake_scene(context)

	#DECISION - should we clear the bake scene each update?
	#Clear bake scene from meshes (this will remove the objects that own the meshes as ell)
	for obj in bake_scene.collection.objects:
		bpy.data.meshes.remove(obj.data, do_unlink=True)

	#todo note 1
	for bake_target in ht.bake_target_collection:
		mirror, mt = bake_target.get_mirror_type(ht)
		if mt is constants.MIRROR_TYPE.SECONDARY:
			continue

		source_obj = bake_target.require_object()

		for variant in bake_target.iter_bake_scene_variant_names():

			if variant in bake_scene.objects:
				#Object is already in bake scene - since we clear the bake scene this means two bake targets resolved to the same name
				#TODO - we should validate the state before even starting this operation
				raise Exception('FAIL') #TODO - proper exception

			elif variant in bpy.data.objects:
				#Object is not in bake scene but it does exist, this is a serious issue
				raise Exception(f'Object {variant} already existing') #TODO - proper exception
				#NOTE - this can happen if there is orphaned objects, like if the scene is deleted but not the objects
				#TBD - how should we deal with this situation? Delete conflicting objects? warn user? Instruct user how to resolve situation?

			else:
				#Object is not in bake scene, let's put it there
				new_object = copy_object(source_obj, variant)
				bake_scene.collection.objects.link(new_object)

			#Remove shape keys if we only want a specific one
			if bake_target.shape_key_name:
				for skey in new_object.data.shape_keys.key_blocks:
					if skey.name != bake_target.shape_key_name:
						new_object.shape_key_remove(skey)





#DEPRECHATED
def create_bake_targets_from_shapekeys(operator, context, ht):
	#BUG - User may create multiple bake targets by calling this over and over

	if source := bpy.data.objects.get(ht.source_object):
		shape_keys = source.data.shape_keys.key_blocks

		def create_mirror(primary, secondary):
			new = ht.bake_target_mirror_collection.add()
			new.primary = primary
			new.secondary = secondary
			return new

		#TODO - Here we should run our rules for the naming scheme

		#Create all targets
		targets = dict()
		mirror_list = list()
		for sk in shape_keys:
			key = sk.name
			targets[key] = intermediate.pending.bake_target(
				name = f'{ht.source_object}_{key}',
				object_name = ht.source_object,
				shape_key_name = key,
				uv_mode = 'UV_IM_MONOCHROME',
			)



		#Configure targets and mirrors
		for key, target in targets.items():
			if key.endswith('_L'):
				base = key[:-2]
				Rk = f'{base}_R'
				R = targets.get(Rk)

				if R:
					mirror_list.append(intermediate.mirror(target, R))

				else:
					log.error(f"Could not create mirror for {key} since there was no such object `{Rk}´")

			elif key.endswith('_R'):
				pass

			elif key.endswith('__None'):
				target.uv_mode = 'UV_IM_NIL'



		#NOTE - there is a bug where we can only set uv_mode (or any other enum) once from the same context.
		#		To avoid this bug we first create dicts that represents the new bake targets and then we instanciate them below
		for target in targets.values():
			new = ht.bake_target_collection.add()
			for key, value in iter_dc(target):
				setattr(new, key, value)

			target.bake_target = new

		#Create mirrors
		for mirror in mirror_list:
			create_mirror(ht.get_bake_target_index(mirror.primary.bake_target), ht.get_bake_target_index(mirror.secondary.bake_target))



class bake_mirrors:
	def set_primary(operator, context, ht):
		if mirror := ht.get_selected_mirror():
			if bake_target := ht.get_selected_bake_target():
				mirror.primary = ht.get_bake_target_index(bake_target)

	def set_secondary(operator, context, ht):
		if mirror := ht.get_selected_mirror():
			if bake_target := ht.get_selected_bake_target():
				mirror.secondary = ht.get_bake_target_index(bake_target)

	def add(operator, context, ht):
		generic_list.add(ht.bake_target_mirror_collection, a_get(ht, 'selected_bake_target_mirror'), a_set(ht, 'selected_bake_target_mirror'))

	def remove(operator, context, ht):
		generic_list.remove(ht.bake_target_mirror_collection, a_get(ht, 'selected_bake_target_mirror'), a_set(ht, 'selected_bake_target_mirror'))

class bake_targets:
	#BUG - currently we don't check if a target is in a mirror and therefore a mirror will point to the wrong thing if removing a reference

	def add(operator, context, ht):
		generic_list.add(ht.bake_target_collection, a_get(ht, 'selected_bake_target'), a_set(ht, 'selected_bake_target'))

	def remove(operator, context, ht):
		generic_list.remove(ht.bake_target_collection, a_get(ht, 'selected_bake_target'), a_set(ht, 'selected_bake_target'))

	def edit_selected(operator, context, ht):
		bake_target = ht.get_selected_bake_target()
		if not bake_target:
			return

		bto = bake_target.get_object()
		if not bto:
			return

		work_scene = get_work_scene(context)
		set_scene(context, work_scene)
		view_layer = context.view_layer
		set_selection(view_layer.objects, bto)
		if bake_target.shape_key_name:
			bto.active_shape_key_index = bto.data.shape_keys.key_blocks.find(bake_target.shape_key_name) #tech-note 4

		bpy.ops.object.mode_set(mode='EDIT')

class bake_groups:

	def add(operator, context, ht):
		generic_list.add(ht.bake_group_collection, a_get(ht, 'selected_bake_group'), a_set(ht, 'selected_bake_group'))

	def remove(operator, context, ht):
		generic_list.remove(ht.bake_group_collection, a_get(ht, 'selected_bake_group'), a_set(ht, 'selected_bake_group'))


	class members:
		def add(operator, context, ht):
			if bake_group := ht.get_selected_bake_group():
				if bake_target := ht.get_selected_bake_target():
					new = generic_list.add(bake_group.members, a_get(bake_group, 'selected_member'), a_set(bake_group, 'selected_member'))
					new.target = ht.get_bake_target_index(bake_target)

		def remove(operator, context, ht):
			if bake_group := ht.get_selected_bake_group():
				generic_list.remove(bake_group.members, a_get(bake_group, 'selected_member'), a_set(bake_group, 'selected_member'))


class bake_variants:

	def add(operator, context, ht):
		if bake_target := ht.get_selected_bake_target():
			generic_list.add(bake_target.variant_collection, a_get(bake_target, 'selected_variant'), a_set(bake_target, 'selected_variant'))

	def remove(operator, context, ht):
		if bake_target := ht.get_selected_bake_target():
			generic_list.remove(bake_target.variant_collection, a_get(bake_target, 'selected_variant'), a_set(bake_target, 'selected_variant'))


def generic_switch_to_material(context, ht, material_type):
	bake_scene = get_bake_scene(context)
	#todo note 1
	for bt in ht.bake_target_collection:
		mirror, mt = bt.get_mirror_type(ht)
		if mt is MIRROR_TYPE.SECONDARY:
			continue

		atlas = bt.get_atlas()
		uv_map = bt.uv_map

		if atlas and uv_map:
			variant_materials = get_material_variants(bt, bake_scene, atlas, uv_map)

			for variant_name, variant in bt.iter_bake_scene_variants():
				target = require_named_entry(bake_scene.objects, variant_name)
				materials = variant_materials[variant_name]
				# set active material
				target.active_material = bpy.data.materials[getattr(materials, material_type)]
		else:
			log.warning(f'{bt.identifier} lacks atlas or uv_map')


def transfer_variant(source, dest):
	dest.name = source.name
	dest.image = source.image
	dest.uv_map = source.uv_map

def copy_collection(source, dest, transfer):
	while len(dest):
		dest.remove(0)

	for item in source:
		transfer(item, dest.add())

def synchronize_mirrors(operator, context, ht):
	for mirror in ht.bake_target_mirror_collection:
		primary = ht.bake_target_collection[mirror.primary]
		secondary = ht.bake_target_collection[mirror.secondary]
		if primary and secondary:
			secondary.uv_area_weight = primary.uv_area_weight
			secondary.uv_mode = primary.uv_mode
			secondary.atlas = primary.atlas
			secondary.uv_map = primary.uv_map
			secondary.multi_variants = primary.multi_variants
			copy_collection(primary.variant_collection, secondary.variant_collection, transfer_variant)
			secondary.selected_variant = primary.selected_variant

def switch_to_bake_material(operator, context, ht):
	generic_switch_to_material(context, ht, 'bake')

def switch_to_preview_material(operator, context, ht):
	generic_switch_to_material(context, ht, 'preview')




class devtools:
	def get_node_links(operator, context, ht):
		link_ref = lambda node, socket: f'{node.name}.{socket.name.replace(" ", "-")}'
		int_tuple = lambda t: tuple(int(e) for e in t)

		if not context.selected_nodes:
			return

		#There might not be an active node so we will use first node in selection instead
		#node_tree = context.active_node.id_data
		node_tree = context.selected_nodes[0].id_data

		result = list()
		result.append('#Node definitions')
		for node in context.selected_nodes:
			result.append(f'{node.bl_idname}\t{node.name}')
		result.append('')

		result.append('#Node locations')
		for node in context.selected_nodes:
			result.append(f'{node.name}.location = {int_tuple(node.location)}')
		result.append('')

		result.append('#Node links')
		for link in node_tree.links:
			result.append(f'{link_ref(link.from_node, link.from_socket)} --> {link_ref(link.to_node, link.to_socket)}')


		body = textwrap.indent('\n'.join(result), '\t')
		log.info(f'Node data:\n\n{body}')