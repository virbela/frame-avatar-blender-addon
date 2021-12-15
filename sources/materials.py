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



# TODO ADD NEW UV!
# 	#Node definitions
# 	ShaderNodeUVMap	baking_uv
# 	ShaderNodeUVMap	baking_uv.001
# 	ShaderNodeTexImage	diffuse_image
# 	ShaderNodeAmbientOcclusion	baking_ao
# 	ShaderNodeBsdfPrincipled	baking_ao_p
# 	ShaderNodeOutputMaterial	baking_out
# 	ShaderNodeTexImage	baking_image

# 	#Node locations
# 	baking_uv.location = (-1130, 171)
# 	baking_uv.001.location = (-1121, -177)
# 	diffuse_image.location = (-869, -31)
# 	baking_ao.location = (-450, 40)
# 	baking_ao_p.location = (-200, 40)
# 	baking_out.location = (95, 37)
# 	baking_image.location = (-873, 301)

# 	#Node links
# 	baking_uv.UV --> baking_image.Vector
# 	baking_ao.Color --> baking_ao_p.Base-Color
# 	baking_ao_p.BSDF --> baking_out.Surface
# 	diffuse_image.Color --> baking_ao.Color
# 	baking_uv.001.UV --> diffuse_image.Vector



setup_bake_material2 = load_node_setup_function('setup_bake_material', '''

	arguments: atlas, uv_map='UVMap', diffuse_input=None

	#Node definitions
	ShaderNodeTexImage      		baking_image
	ShaderNodeUVMap 				baking_uv
	ShaderNodeOutputMaterial        baking_out
	ShaderNodeBsdfPrincipled        baking_ao_p
	ShaderNodeAmbientOcclusion      baking_ao
	if diffuse_input:
		ShaderNodeTexImage      	diffuse_image

	#Node locations
	baking_image.location = 		(-873, 301)
	baking_uv.location = 			(-1326, -34)
	baking_out.location = 			(95, 37)
	baking_ao_p.location = 			(-200, 40)
	baking_ao.location = 			(-450, 40)
	if diffuse_input:
		diffuse_image.location = 	(-869, -31)

	#Other settings
	baking_image.image = atlas
	baking_uv.uv_map = uv_map
	if diffuse_input:
		diffuse_image.image = diffuse_input

	#Node links
	baking_uv.UV --> baking_image.Vector
	baking_ao.Color --> baking_ao_p.Base-Color
	baking_ao_p.BSDF --> baking_out.Surface
	baking_uv.UV --> diffuse_image.Vector

	if diffuse_input:
		diffuse_image.Color --> baking_ao.Color

''')




