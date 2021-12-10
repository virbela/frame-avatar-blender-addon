import bpy
from . import utilities
from .helpers import enum_descriptor, frame_property_group

#Important notes
#	Regarding descriptions of properties, please see contribution note 1

#TODO - Add descriptions for all properties

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




class BakeVariant(frame_property_group):
	name: 					bpy.props.StringProperty(name="Variant name", default='Untitled variant')
	image:					bpy.props.StringProperty(name="Image texture")


class BakeTarget(frame_property_group):

	name: 					bpy.props.StringProperty(name = "Bake target name", default='Untitled bake target')

	object_name: 			bpy.props.StringProperty(
		name = 					"Object name",
		description = 			"The object that is used for this bake target.\n"
								"Once selected it is possible to select a specific shape key",
	)
	shape_key_name: 		bpy.props.StringProperty(name="Shape key")

	uv_area_weight: 		bpy.props.FloatProperty(name="UV island area weight", default=1.0)


	uv_mode:				bpy.props.EnumProperty(items=tuple(UV_ISLAND_MODES), name="UV island mode", default=0)

	atlas:					bpy.props.StringProperty(name="Atlas name")
	# ↑ This is used for storing the automatic choice as well as the manual (frozen) one
	uv_set:					bpy.props.StringProperty(name="UV set", default='UVMap')


	#Variants
	multi_variants:			bpy.props.BoolProperty(name="Multiple variants", default=False)
	variant_collection:		bpy.props.CollectionProperty(type = BakeVariant)
	selected_variant:		bpy.props.IntProperty(name = "Selected bake variant", default = -1)



	@property	#contribution note 8
	def identifier(self):
		if self.object_name:
			if self.shape_key_name:
				return f'{self.object_name}.{self.shape_key_name}'
			else:
				return self.object_name


	#TODO implement
	def get_mirror_type(self, ht):
		for mirror in ht.bake_target_mirror_collection:
			print(mirror.primary)



class BakeTargetMirrorEntry(frame_property_group):
	#Here I wanted to use PointerProperty but they don't really act as the name implies. See contribution note 7 for more details.
	primary: 		bpy.props.StringProperty(name='Primary bake target')
	secondary: 		bpy.props.StringProperty(name='Secondary bake target')


class HomeomorphicProperties(frame_property_group):

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

	def get_selected_bake_target(self):
		if self.selected_bake_target != -1:
			return self.bake_target_collection[self.selected_bake_target]

	def get_selected_mirror(self):
		if self.selected_bake_target_mirror != -1:
			return self.bake_target_mirror_collection[self.selected_bake_target_mirror]

