import bpy
from .utilities import deselect_all_nodes, get_named_image
from .exceptions import *
from .logging import log_writer
from .helpers import get_work_scene
from .constants import *

def pack_uv_islands(context):
	pass

def get_bake_group(bake_target):
	#TODO implement
	return [bake_target]

def bake_all_bake_targets(context):
	#TODO - implement!
	pass


def perform_baking(context, baking_scene, bake_group):


	#TODO - We only need to setup the bake material once per bake but we need to assign the material to each bake object in the group - we should make sure this is what happens
	#TODO - We should probably just assign the bake material instead of complaining if bake object does not have an active material

	for bake_target in bake_group:
		bake_object = baking_scene.objects[bake_target.name]

		active_mat = bake_object.active_material
		if not active_mat:
			raise BakeException.NoActiveMaterial(bake_object)

		active_mat.use_nodes = True

		#TODO - check if we should really do this here
		create_intermediate_bake_texture_nodes(active_mat, atlas, uv_set)

		baking_scene.context.view_layer.objects.active = bake_object
		baking_scene.context.view_layer.objects[bake_object.name].select_set(True)

	bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')


def bake_selected_bake_targets(context):
	#TODO - implement!

	#TODO - better abstraction - less code duplication (for when getting the scenes and such)

	with log_writer(context) as log:

		prepare_batch_bake()

		work_scene = get_work_scene(context)
		if not work_scene:
			raise BakeException.NoSuchScene(WORK_SCENE)

		baking_scene = bpy.data.scenes.get(BAKE_SCENE)
		if not baking_scene:
			raise BakeException.NoSuchScene(BAKE_SCENE)

		HT = work_scene.homeomorphictools
		bake_target = HT.bake_target_collection[HT.selected_bake_target]
		#bake_object = baking_scene.objects[bake_target.name]
		#bake_material = create_bake_material(BAKE_MATERIAL)

		bake_group = get_bake_group(bake_target)

		#log.debug(f'Baking target {bake_target} using object {bake_object} with material {bake_material}.')
		log.debug(f'The following objects are in the bake group: {", ".join(b.name for b in bake_group)}')


		perform_baking(context, baking_scene, bake_group)

def update_bake_scene(context):
	with log_writer(context) as log:
		if work_scene := get_work_scene(context):

			#BUG - must check if baking objects already exists - especially since SomeBakeTarget would be named SomeBakeTarget001 or similar if there is name colissions
			baking_scene = bpy.data.scenes.get(BAKE_SCENE) or bpy.data.scenes.new(BAKE_SCENE)

			#DECISION - should we clear the scene?
			for scene_obj in baking_scene.collection.objects:
				baking_scene.collection.objects.unlink(scene_obj)

			for bake_target in work_scene.homeomorphictools.bake_target_collection:

				name = bake_target.object_name
				shape_key = bake_target.shape_key_name

				#Fetch object to copy
				obj = work_scene.objects.get(name)
				new_object = obj.copy()
				new_object.data = obj.data.copy()	#Copy data as well
				new_object.name = bake_target.name


				#Remove all shape keys except the selected one
				if shape_key:
					for skey in new_object.data.shape_keys.key_blocks:
						if skey.name != shape_key:
							new_object.shape_key_remove(skey)

				#Put object in baking scene
				baking_scene.collection.objects.link(new_object)



				#DECISION - maybe this should not even be handled right here but rather when executing baking
				#TODO - don't even bother switching scene here if we don't have operations to perform
				context.window.scene = baking_scene
				context.view_layer.objects.active = new_object
				bpy.ops.object.mode_set(mode='EDIT', toggle=False)
				bpy.ops.mesh.select_all(action='SELECT')
				#TODO - make this an optional part of the workflow
				bpy.ops.mesh.average_normals(average_type='FACE_AREA')		#Fix up weird normals
				#TODO - make this an optional part of the workflow
				bpy.ops.mesh.normals_make_consistent(inside=False)			#Make normals consistent
				bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
				context.view_layer.objects.active = None
				context.window.scene = work_scene


			log.info(f'Created baking scene `{BAKE_SCENE}´ with {len(baking_scene.collection.objects)} objects.')


def create_bake_targets_from_shapekeys(context, tool_properties, shape_keys):

	with log_writer(context) as log:
		#BUG - User may create multiple bake targets

		def create_mirror(primary, secondary):
			new = tool_properties.bake_target_mirror_collection.add()
			source = tool_properties.source_object
			new.primary = f'{source}.{primary}'
			new.secondary = f'{source}.{secondary}'
			return new


		#TODO - Here we should run our rules for the naming scheme

		#Create all targets
		targets = dict()
		for sk in shape_keys:
			key = sk.name
			targets[key] = dict(
				name = f'bake_{tool_properties.source_object}_{key}',
				object_name = tool_properties.source_object,
				shape_key_name = key,
				uv_mode = 'UV_IM_MONOCHROME',
			)



		#Configure targets and mirrors
		for key in targets:
			if key.endswith('_L'):
				base = key[:-2]
				Lk = f'{base}_L'
				Rk = f'{base}_R'
				R = targets.get(Rk)

				if R:
					create_mirror(Lk, Rk)
				else:
					log.error(f"Could not create mirror for {key} since there was no such object `{Rk}´")

			elif key.endswith('_R'):
				pass

			elif key.endswith('__None'):
				targets[key]['uv_mode'] = 'UV_IM_NIL'


		#NOTE - there is a bug where we can only set uv_mode (or any other enum) once from the same context.
		#		To avoid this bug we first create dicts that represents the new bake targets and then we instanciate them below
		for target in targets.values():
			new = tool_properties.bake_target_collection.add()
			for key, value in target.items():
				setattr(new, key, value)


def create_bake_material(name):
	'''
		Creates material for baking

			Ambient Occlusion.Color → Principled BSDF.Base Color
			Principled BSDF.BSDF → Material Output.Surface

	'''

	if bakematerial := bpy.data.materials.get(name):
		return bakematerial
	else:

		bakematerial = bpy.data.materials.new(name)
		bakematerial.use_nodes = True

		node_bsdf = bakematerial.node_tree.nodes.get('Principled BSDF')
		node_ao = bakematerial.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
		node_ao.location = (-463, 39)

		bakematerial.node_tree.links.new(node_bsdf.inputs['Base Color'], node_ao.outputs['Color'])

		deselect_all_nodes(bakematerial.node_tree.nodes)
		return bakematerial


def create_intermediate_bake_texture_nodes(active_mat, atlas, uv_set):
	nodes = active_mat.node_tree.nodes
	deselect_all_nodes(nodes)

	if texture_node := nodes.get('bake_texture_node'):
		pass
	else:
		texture_node = nodes.new('ShaderNodeTexImage')
		texture_node.name = 'bake_texture_node'
		texture_node.location = (0, 688)
		texture_node.select = True

	texture_node.image = atlas

	# create uv node and connect it to bake target texture node
	# assign the UV set from the "uvset_string" in PropertyGroup
	if uv_node := nodes.get('bake_uv_node'):
		pass
	else:
		uv_node = nodes.new('ShaderNodeUVMap')
		uv_node.name = 'bake_uv_node'
		uv_node.location = (-196, 540)
		active_mat.node_tree.links.new(texture_node.inputs[0], uv_node.outputs[0])

	uv_node.uv_map = uv_set
	nodes.active = texture_node



#DEPRECHATED - this function shall be rewritten but is here for reference
# Add feature baking objects in isolation
def batch_bake(bake_object, atlas, uv_set):


	bpy.context.view_layer.objects.active = bake_object

	bpy.context.scene.cycles.bake_type = 'DIFFUSE'
	bpy.context.scene.render.bake.use_pass_direct = False
	bpy.context.scene.render.bake.use_pass_indirect = False
	bpy.context.scene.render.bake.use_pass_color = True

	active_mat = bake_object.active_material
	if not active_mat:
		raise BakeException.NoActiveMaterial(bake_object)

	active_mat.use_nodes = True

	create_intermediate_bake_texture_nodes(active_mat, atlas, uv_set)

	bpy.context.view_layer.objects.active = bake_object
	bpy.context.view_layer.objects[bake_object.name].select_set(True)

	bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')

	atlas.file_format = 'PNG'
	#If atlas.filepath is used it will complaining about the image "" (empty string) not being available. Not sure why.
	atlas.filepath_raw = f'//{atlas.name}.png'
	atlas.save()


def prepare_batch_bake():
	baking_scene = bpy.data.scenes.get(BAKE_SCENE)
	if not baking_scene:
		raise BakeException.NoSuchScene(BAKE_SCENE)

	bake_scene.cycles.bake_type = 'DIFFUSE'
	bake_scene.render.bake.use_pass_direct = False
	bake_scene.render.bake.use_pass_indirect = False
	bake_scene.render.bake.use_pass_color = True
