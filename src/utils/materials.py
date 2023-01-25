import bpy
from bpy.types import Scene, Image, Material, ShaderNodeTree

from .constants import Assets
from .properties import BakeTarget
from .structures import intermediate
from .node_utils import load_node_setup_function
from .helpers import create_named_entry, require_named_entry, get_nice_name, named_entry_action

def get_material_variants(bt: BakeTarget, bake_scene: Scene, atlas: Image, uv_map: str, recreate: bool = False):

	#ISSUE-7: Material creation needs improvement
	#	*	We should handle the case when multiple variants are not used (we should use a generic naming function that is discussed elsewere).
	#	*	Move out the cache `result` to a module and also document why we need it (do we?)
	#	labels: needs-improvement

	result = dict()
	for variant_name, variant in bt.iter_bake_scene_variants():
		_ = require_named_entry(bake_scene.objects, variant_name)

		if variant.image:
			paint_image = bpy.data.images[variant.image]	#TODO - make sure this image exists
			paint_uv = variant.uv_map

			# we are hitting the 63 char limit here and therefore we use get_nice_name
			bake_material_name = get_nice_name(result, f'bake-{bt.shortname}-{variant.name}', 32)
			preview_material_name = get_nice_name(result, f'preview-{bt.shortname}-{variant.name}', 32)

			bake_material = create_named_entry(bpy.data.materials, bake_material_name, action=named_entry_action.RECREATE if recreate else named_entry_action.GET_EXISTING)
			bake_material.use_nodes = True	#contribution note 9
			setup_bake_material(bake_material, atlas, uv_map, paint_image, paint_uv)

			preview_material = create_named_entry(bpy.data.materials, preview_material_name, action=named_entry_action.RECREATE if recreate else named_entry_action.GET_EXISTING)
			preview_material.use_nodes = True	#contribution note 9
			setup_bake_preview_material(preview_material, atlas, uv_map)


		else:
			raise Exception('not implemented')	#TODO - implement

		#store what material we are using
		result[variant_name] = intermediate.pending.materials(
			bake = bake_material_name,
			preview = preview_material_name,
		)

	return result


def setup_bake_material(
		material: Material, 
		atlas: Image, uv_map: str ='UVMap', 
		diffuse_image: Image = None, diffuse_uv_map: Image = None) -> None:
	template =  bpy.data.materials[Assets.Materials.BakeAO.name]
	if diffuse_image and diffuse_uv_map:
		template =  bpy.data.materials[Assets.Materials.BakeDiffuse.name]

	copy_nodetree(template.node_tree, material.node_tree)

	nodes = material.node_tree.nodes
	nodes['tex_target'].image = atlas
	nodes['uvm_target'].uv_map = uv_map
	if diffuse_image and diffuse_uv_map:
		nodes['tex_diffuse'].image = diffuse_image
		nodes['uvm_diffuse'].uv_map = diffuse_uv_map
	

def setup_bake_preview_material(
		material: Material, 
		atlas: Image, uv_map: str ='UVMap') -> None:
	
	template =  bpy.data.materials[Assets.Materials.BakePreview.name]
	copy_nodetree(template.node_tree, material.node_tree)

	nodes = material.node_tree.nodes
	nodes['tex_target'].image = atlas
	nodes['uvm_target'].uv_map = uv_map


def copy_nodetree(tree_from: ShaderNodeTree, tree_to: ShaderNodeTree) -> None:
	tree_to.nodes.clear()
	tree_to.links.clear()

	# -- copy nodes
	for node in tree_from.nodes:
		new = tree_to.nodes.new(node.bl_idname)
		new.location = node.location
		new.name = node.name

	# -- copy links
	for node in tree_from.nodes:
		to_node = tree_to.nodes[node.name]
		for i, input in enumerate(node.inputs):
			for link in input.links:
				connected_node = tree_to.nodes[link.from_node.name]
				tree_to.links.new(
					connected_node.outputs[link.from_socket.name],
			    	to_node.inputs[i]
				)


setup_bake_material_old = load_node_setup_function('setup_bake_material', '''

	arguments: atlas, uv_map='UVMap', diffuse_image=None, diffuse_uv_map=None

	#Node definitions
	ShaderNodeUVMap				uvm_target
	ShaderNodeAmbientOcclusion	ao
	ShaderNodeBsdfPrincipled	nbp_ao
	ShaderNodeOutputMaterial	out
	ShaderNodeTexImage			tex_target

	#Node locations
	uvm_target.location = 		(-1130, 171)
	ao.location = 				(-450, 40)
	nbp_ao.location = 			(-200, 40)
	out.location = 				(95, 37)
	tex_target.location = 		(-873, 301)

	#Node links
	uvm_target.UV 		--> 	tex_target.Vector
	ao.Color 			--> 	nbp_ao.Base-Color
	nbp_ao.BSDF 		--> 	out.Surface

	#Settings
	tex_target.image = atlas
	uvm_target.uv_map = uv_map


	#For diffuse source
	if diffuse_image and diffuse_uv_map:

		ShaderNodeUVMap				uvm_diffuse
		ShaderNodeTexImage			tex_diffuse

		uvm_diffuse.location = 		(-1121, -177)
		tex_diffuse.location = 		(-869, -31)

		uvm_diffuse.UV 		--> 	tex_diffuse.Vector
		tex_diffuse.Color 	--> 	nbp_ao.Base-Color

		tex_diffuse.image = diffuse_image
		uvm_diffuse.uv_map = diffuse_uv_map

	clear_selection()
	set_active(tex_target)
''')


setup_bake_preview_material = load_node_setup_function('setup_bake_preview_material', '''

	arguments: atlas, uv_map='UVMap'

	#Node definitions
	ShaderNodeUVMap				uvm_target
	ShaderNodeOutputMaterial	out
	ShaderNodeTexImage			tex_target

	#Node locations
	uvm_target.location = 		(-1130, 171)
	out.location = 				(95, 37)
	tex_target.location = 		(-873, 301)

	#Node links
	uvm_target.UV 		--> 	tex_target.Vector
	tex_target.Color	--> 	out.Surface

	#Settings
	tex_target.image = atlas
	uvm_target.uv_map = uv_map

	clear_selection()
	clear_active()
''')
