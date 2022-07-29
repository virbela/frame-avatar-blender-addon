import bpy
from .structures import intermediate
from .node_utils import load_node_setup_function
from .helpers import create_named_entry, require_named_entry, get_nice_name, named_entry_action

def get_material_variants(bt, bake_scene, atlas, uv_map, recreate=False):

	#ISSUE-7: Material creation needs improvement
	#	*	We should handle the case when multiple variants are not used (we should use a generic naming function that is discussed elsewere).
	#	*	Move out the cache `result` to a module and also document why we need it (do we?)
	#	labels: needs-improvement

	result = dict()
	for variant_name, variant in bt.iter_bake_scene_variants():
		target = require_named_entry(bake_scene.objects, variant_name)

		if variant.image:
			paint_image = bpy.data.images[variant.image]	#TODO - make sure this image exists
			paint_uv = variant.uv_map

			# we are hitting the 63 char limit here and therefore we use get_nice_name
			bake_material_name = get_nice_name(result, f'bake-{bt.shortname}-{variant.name}', 32)
			preview_material_name = get_nice_name(result, f'preview-{bt.shortname}-{variant.name}', 32)

			bake_material = create_named_entry(bpy.data.materials, bake_material_name, action=named_entry_action.RECREATE if recreate else named_entry_action.GET_EXISTING)
			bake_material.use_nodes = True	#contribution note 9
			setup_bake_material(bake_material.node_tree, atlas, uv_map, paint_image, paint_uv)

			preview_material = create_named_entry(bpy.data.materials, preview_material_name, action=named_entry_action.RECREATE if recreate else named_entry_action.GET_EXISTING)
			preview_material.use_nodes = True	#contribution note 9
			setup_bake_preview_material(preview_material.node_tree, atlas, uv_map)


		else:
			raise Exception('not implemented')	#TODO - implement

		#store what material we are using
		result[variant_name] = intermediate.pending.materials(
			bake = bake_material_name,
			preview = preview_material_name,
		)

	return result



#TO-DOC		How this works is not yet documented, it is an experimental feature meant to make it much easier to define materials programatically for use in automation
# Brief documentation has been create in docs/node-dsl


setup_bake_material = load_node_setup_function('setup_bake_material', '''

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



setup_rgb_channel_packing_material = load_node_setup_function('setup_rgb_channel_packing_material', '''

	arguments: r_image, g_image, b_image, color_image, target_image, uv_map

	#Node definitions
	ShaderNodeTexImage              target
	ShaderNodeOutputMaterial        output
	ShaderNodeBsdfDiffuse           diffuse
	ShaderNodeCombineRGB            combine
	ShaderNodeUVMap                 uv_map_node
	ShaderNodeTexImage              source_b
	ShaderNodeTexImage              source_g
	ShaderNodeTexImage              source_r

	#Node locations
	target.location =               (-80, 760)
	output.location =               (720, 300)
	diffuse.location =              (520, 300)
	combine.location =              (320, 300)
	uv_map_node.location =          (-380, 180)
	source_b.location =             (-80, -20)
	source_g.location =             (-80, 240)
	source_r.location =             (-80, 500)

	#Node links
	uv_map_node.UV       --> source_r.Vector
	uv_map_node.UV       --> source_g.Vector
	uv_map_node.UV       --> source_b.Vector
	uv_map_node.UV       --> target.Vector

	source_r.Color  --> combine.R
	source_g.Color  --> combine.G
	source_b.Color  --> combine.B

	source_r.image = r_image
	source_g.image = g_image
	source_b.image = b_image
	target.image = target_image

	uv_map_node.uv_map = uv_map

	diffuse.BSDF    --> output.Surface
	combine.Image   --> diffuse.Color

	clear_selection()
	set_active(target)

''')

#TODO - intermediate textures should be linear float textures
