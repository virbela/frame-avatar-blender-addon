import bpy
from .utilities import deselect_all_nodes, get_named_image
from .exceptions import *


def create_bake_targets_from_shapekeys(tool_properties, shape_keys):

	def create_mirror(primary, secondary):
		new = tool_properties.bake_target_mirror_collection.add()
		new.primary = primary
		new.secondary = secondary
		return new

	def create_target(name, mode='UV_IM_MONOCHROME'):
		new = tool_properties.bake_target_collection.add()
		new.object_name = tool_properties.source_object
		new.shape_key_name = name
		return new

	for sk in shape_keys:
		key = sk.name
		#TODO
		#Here we should run our rules for the naming scheme

		if key.endswith('_L'):
			base = key[:-2]
			L, R = f'{base}_L', f'{base}_R'
			create_target(L)
			create_target(R)
			create_mirror(L, R)

		elif key.endswith('_R'):
			pass

		elif key.endswith('__None'):
			base = key[:-6]
			create_target(base, 'UV_IM_NIL')

		else:
			create_target(key)



def create_bake_material(name):
	'''
		Creates material for baking

			Ambient Occlusion.Color → Principled BSDF.Base Color
			Principled BSDF.BSDF → Material Output.Surface

	'''

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