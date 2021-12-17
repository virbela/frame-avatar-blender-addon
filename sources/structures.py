#This module is used to define common structures that are only used internally in certain operations.
#These must not be saved in any blender specific context and must be discarded after use
#For structures that SHOULD be saved in blender specific contexts are defined in the properties.py module.

from dataclasses import dataclass, asdict as dc_to_dict

def iter_dc(d):
	return dc_to_dict(d).items()

class intermediate:
	# it would be nice to specify these members more fully but the problem is that we can't both define a tree structure AND refer to things in the tree in
	# a satisfying way. Since we are not using typing now anyway we will let it be like this. It wouldn't hurt to add comments though that explains the proper type

	class pending:
		@dataclass
		class bake_target:
			name: 				str
			object_name: 		str
			shape_key_name: 	str
			uv_mode: 			str
			bake_target:		object		= None

		@dataclass
		class materials:
			bake:				str
			preview:			str


	class packing:
		@dataclass
		class bake_target:
			bake_target:		object	#properties.BakeTarget
			bake_object:		object	#the object in the bake scene
			area:				float		= 0.0
			variant_name:		str			= None

	@dataclass
	class mirror:
		primary: 				object	#intermediate.pending.bake_target
		secondary: 				object	#intermediate.pending.bake_target



