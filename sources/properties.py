import bpy
from . import utilities
from .helpers import enum_descriptor, base_property_group

UV_ISLAND_MODES = enum_descriptor(

	#Icons: https://blenderartists.org/uploads/default/original/4X/7/a/6/7a6b22e5e0fa4d2108dddc58c84c8b3d5e36e0ee.png

	#Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
	#(identifier, 			name, 				description,
	#	icon, 				number),

	#NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
	#compact and nice table.

	('UV_IM_MONOCHROME',	'Grayscale',		'This UV island will be channel packed to a grayscale segment of the atlas',
		'IMAGE_ZDEPTH',		0),

	('UV_IM_COLOR',			'Color',			'This UV island will end up on the color segment of the atlas',
		'COLOR',			1),

	('UV_IM_NIL',			'Nil UV island',	'This UV island will have zero area (unshaded)',
		'DOT',				2),

	('UV_IM_FROZEN',		'Frozen',			'This UV island will not be modified by the packer',
		'FREEZE',			3),
)





@utilities.register_class
class BakeVariant(base_property_group):
	name: 					bpy.props.StringProperty(name="Variant name", default='Untitled variant')
	image:					bpy.props.StringProperty(name="Image texture")


@utilities.register_class
class BakeTarget(base_property_group):

	#BUG these targets aren't properly named so we can't sort them, they all seem to be empty string


	# def _get_name(arg):
	# 	print('GET', arg)
	# 	return '123'

	name: 					bpy.props.StringProperty(name="Bake target name")

	object_name: 			bpy.props.StringProperty(name="Object name")
	shape_key_name: 		bpy.props.StringProperty(name="Shape key")

	uv_area_weight: 		bpy.props.FloatProperty(name="UV island area weight", default=1.0)


	uv_mode:				bpy.props.EnumProperty(items=tuple(UV_ISLAND_MODES), name="UV island mode", default=0)

	auto_atlas:				bpy.props.BoolProperty(name="Assign atlas automatically", default=True)
	atlas:					bpy.props.StringProperty(name="Atlas name")
	# ↑ This is used for storing the automatic choice as well as the manual
	uv_set:					bpy.props.StringProperty(name="UV set", default='UVMap')


	#Variants
	multi_variants:			bpy.props.BoolProperty(name="Multiple variants", default=False)
	variant_collection:		bpy.props.CollectionProperty(type = BakeVariant)
	selected_variant:		bpy.props.IntProperty(name = "Selected bake variant", default = -1)



	@property
	def identifier(self):
		if self.object_name:
			if self.shape_key_name:
				return f'{self.object_name}.{self.shape_key_name}'
			else:
				return self.object_name



@utilities.register_class
class BakeTargetMirrorEntry(base_property_group):
	primary: 		bpy.props.StringProperty(name='Primary bake target')
	secondary:		bpy.props.StringProperty(name='Secondary bake target')


@utilities.register_class
class HomeomorphicProperties(base_property_group):

	### Bake targets ###

	#Note that we use -1 to indicate that nothing is selected for integer selections
	bake_target_collection: 			bpy.props.CollectionProperty(type = BakeTarget)
	selected_bake_target: 				bpy.props.IntProperty(name = "Selected bake target", default = -1)

	bake_target_mirror_collection: 		bpy.props.CollectionProperty(type = BakeTargetMirrorEntry)
	selected_bake_target_mirror: 		bpy.props.IntProperty(name = "Selected mirror entry", default = -1)

	source_object: 						bpy.props.StringProperty(name="Object name")

	### Atlas,textures, paint assist ###
	atlas_size: 						bpy.props.IntProperty(name="Atlas size", default = 4096)
	color_percentage:					bpy.props.FloatProperty(name="Atlas color region percentage", default = 25.0)

	painting_size:						bpy.props.IntProperty(name="Hand paint texture size", default = 1024)