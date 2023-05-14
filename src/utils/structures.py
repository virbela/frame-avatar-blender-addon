"""
This module is used to define common structures that are only used internally in certain operations.
These must not be saved in any blender specific context and must be discarded after use
For structures that SHOULD be saved in blender specific contexts are defined in the properties.py module.
"""

from dataclasses import dataclass

def iter_dc(d):
    # note: dataclasses.asdict performs a deep copy which will be problematic when referencing blender objects so we will iter it ourselves
    return ((key, getattr(d, key)) for key in d.__dataclass_fields__)


class intermediate:
    class pending:
        @dataclass
        class bake_target:
            name: 				str
            object_name: 		str
            source_object:		object
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
            bake_target:		object
            variant:			object
            area:				float		= 0.0
            variant_name:		str			= None
            bin:				object		= None

        @dataclass
        class atlas_bin:
            name:				str
            allocated:			float		= 0.0
            atlas:				object		= None

    @dataclass
    class mirror:
        primary: 				object	#intermediate.pending.bake_target
        secondary: 				object	#intermediate.pending.bake_target



