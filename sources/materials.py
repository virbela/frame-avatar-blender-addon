from .node_utils import load_node_setup_function



#TO-DOC		How this works is not yet documented, it is an experimental feature meant to make it much easier to define materials programatically for use in automation
# Brief documentation has been create in docs/node-dsl

setup_bake_material = load_node_setup_function('setup_bake_material', '''

	#This function signature as ammended to the (_tree) signature that this function will get
	arguments: atlas, uv_map='UVMap'

	#Define nodes
	ShaderNodeTexImage 				img				baking_image
	ShaderNodeUVMap					uv				baking_uv

	ShaderNodeBsdfPrincipled		ao_p			baking_ao_p
	ShaderNodeAmbientOcclusion		ao				baking_ao
	ShaderNodeOutputMaterial		out				baking_out


	#Setup node locations (just to prevent them from forming a heap)
	ao.location = (-450, 40)
	ao_p.location = (-200, 40)
	out.location = (100, 40)
	img.location = (0, 700)
	uv.location = (-200, 500)

	#Setup node settings
	img.image = atlas
	uv.uv_map = uv_map

	#Make connections
	uv.UV --> img.Vector
	ao.Color --> ao_p.Base-Color
	ao_p.BSDF --> out.Surface

	#Set img node to be the active one
	set_selection(img)	#TBD Do we need selection or only active?
	set_active(img)

''')






setup_bake_material2 = load_node_setup_function('setup_bake_material', '''

	arguments: atlas, uv_map='UVMap', diffuse_image=None, diffuse_uv_map='Diffuse'

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
	if diffuse_image:

		ShaderNodeUVMap				uvm_diffuse
		ShaderNodeTexImage			tex_diffuse

		uvm_diffuse.location = 		(-1121, -177)
		tex_diffuse.location = 		(-869, -31)

		uvm_diffuse.UV 		--> 	tex_diffuse.Vector
		tex_diffuse.Color 	--> 	ao.Color

		tex_diffuse.image = diffuse_image
		uvm_diffuse.uv_map = diffuse_uv_map

	set_active(tex_target)


''')




