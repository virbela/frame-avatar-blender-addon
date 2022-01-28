import bpy
from .helpers import enum_descriptor, frame_property_group, get_named_entry, require_named_entry, get_bake_scene, register_class
from .constants import MIRROR_TYPE
from .exceptions import InternalError

#Important notes
#	Regarding descriptions of properties, please see contribution note 1

#TODO - Add descriptions for all properties

UV_ISLAND_MODES = enum_descriptor(

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


UV_MIRROR_AXIS = enum_descriptor(

	#Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
	#(identifier, 			name, 				description,
	#	icon, 				number),

	#NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
	#compact and nice table.

	('UV_MA_U',				'U',				'U (X) Axis',
		'EVENT_U',			0),

	('UV_MA_V',				'V',				'V (Y) Axis',
		'EVENT_V',			1),

)


# GEOMETRY_MIRROR_AXIS = enum_descriptor(		#MAYBE-LATER

# 	#Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
# 	#(identifier, 			name, 				description,
# 	#	icon, 				number),

# 	#NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
# 	#compact and nice table.

# 	('GEOM_MA_X',			'X',				'X Axis',
# 		'EVENT_X',			0),

# 	('GEOM_MA_Y',			'Y',				'Y Axis',
# 		'EVENT_Y',			1),

# 	('GEOM_MA_Z',			'Z',				'Z Axis',
# 		'EVENT_Z',			2),
# )

UV_BAKE_MODE = enum_descriptor(

	#Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
	#(identifier, 			name, 				description,
	#	icon, 				number),

	#NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
	#compact and nice table.

	('UV_BM_REGULAR',		'Regular',			'This is a regular, non mirrored, bake target',
		'OBJECT_DATA',		0),

	('UV_BM_MIRRORED',		'Mirrored',			'This bake target will be mirrored upon another target along the U axis',
		'MOD_MIRROR',		1),
)


UV_TARGET_CHANNEL = enum_descriptor(

	#Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
	#(identifier, 			name, 				description,
	#	icon, 				number),

	#NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
	#compact and nice table.

	('UV_TARGET_NIL',		'Unassigned',			'UV island has not yet been assigned an atlas channel',
		'DOT',				0),

	('UV_TARGET_COLOR',		'Color channel',		'UV island will be placed in the color channel',
		'COLOR',			1),

	('UV_TARGET_R',			'Red channel',			'UV island will be placed in the red channel',
		'EVENT_R',			2),

	('UV_TARGET_G',			'Green channel',		'UV island will be placed in the green channel',
		'EVENT_G',			3),

	('UV_TARGET_B',			'Blue channel',			'UV island will be placed in the blue channel',
		'EVENT_B',			4),
)



class BakeVariant(frame_property_group):
	name: 					bpy.props.StringProperty(name="Variant name", default='Untitled variant')
	image:					bpy.props.PointerProperty(name="Image texture", type=bpy.types.Image)
	uv_map:					bpy.props.StringProperty(name="UV Map")

	workmesh:				bpy.props.PointerProperty(name='Work mesh', type=bpy.types.Object)

	#NOTE - we are not caring about target channel right now - we instead use intermediate_atlas
	uv_target_channel:				bpy.props.EnumProperty(items=tuple(UV_TARGET_CHANNEL), name="UV target channel", default=0)
	intermediate_atlas:				bpy.props.PointerProperty(name='Intermediate atlas', type=bpy.types.Image)


class BakeTarget(frame_property_group):

	name: 					bpy.props.StringProperty(name = "Bake target name", default='Untitled bake target')

	object_name: 			bpy.props.StringProperty(
		name = 					"Object name",
		description = 			"The object that is used for this bake target.\n"
								"Once selected it is possible to select a specific shape key",
	)

	# source info
	source_object:					bpy.props.PointerProperty(name='Source object', type=bpy.types.Object)
	shape_key_name: 				bpy.props.StringProperty(name="Shape key")

	uv_area_weight: 				bpy.props.FloatProperty(name="UV island area weight", default=1.0)

	bake_mode:						bpy.props.EnumProperty(items=tuple(UV_BAKE_MODE), name="UV bake mode", default=0)

	uv_mirror_axis:					bpy.props.EnumProperty(items=tuple(UV_MIRROR_AXIS), name="UV mirror axis", default=0)

	mirror_source:					bpy.props.IntProperty(name='Bake target used for mirror')
	uv_mirror_options_expanded:		bpy.props.BoolProperty(name="UV mirror options expanded", default=True)

	#geom_mirror_axis:				bpy.props.EnumProperty(items=tuple(GEOMETRY_MIRROR_AXIS), name="Geometry mirror axis", default=0)		#MAYBE-LATER

	uv_mode:						bpy.props.EnumProperty(items=tuple(UV_ISLAND_MODES), name="UV island mode", default=0)

	#atlas:							bpy.props.StringProperty(name="Atlas name")
	atlas:							bpy.props.PointerProperty(name="Atlas image", type=bpy.types.Image)
	# ↑ This is used for storing the automatic choice as well as the manual (frozen) one

	#TBD - use this? - yes we need UV map for when rescaling from source
	source_uv_map:					bpy.props.StringProperty(name="UV map", default='UVMap')


	#Variants
	multi_variants:					bpy.props.BoolProperty(name="Multiple variants", default=False)
	variant_collection:				bpy.props.CollectionProperty(type = BakeVariant)
	selected_variant:				bpy.props.IntProperty(name = "Selected bake variant", default = -1)



	def get_object(self):
		return get_named_entry(bpy.data.objects, self.object_name)

	def require_object(self):
		return require_named_entry(bpy.data.objects, self.object_name)

	#def get_bake_scene_object(self, context):
		#bake_scene = get_bake_scene(context)
		#return get_named_entry(bake_scene.objects, self.get_bake_scene_name())

	#def require_bake_scene_object(self, context):
	#	bake_scene = get_bake_scene(context)
	#	return require_named_entry(bake_scene.objects, self.get_bake_scene_name())

	def get_atlas(self):
		return get_named_entry(bpy.data.images, self.atlas)

	def require_atlas(self):
		return require_named_entry(bpy.data.images, self.atlas)



	# @property	#contribution note 8B
	# def identifier(self):
	# 	return str(ht.get_bake_target_index(self))


		# if self.object_name:
		# 	if self.shape_key_name:
		# 		return f'{self.object_name}.{self.shape_key_name}'
		# 	else:
		# 		return self.object_name


	@property
	def shortname(self):
		if self.object_name:
			if self.shape_key_name:
				return self.shape_key_name
			else:
				return self.object_name
		return 'untitled'


	def get_mirror_type(self, ht):
		find_id = ht.get_bake_target_index(self)
		for mirror in ht.bake_target_mirror_collection:
			if find_id == mirror.primary:
				return mirror, MIRROR_TYPE.PRIMARY
			elif find_id == mirror.secondary:
				return mirror, MIRROR_TYPE.SECONDARY

		return None, None


	#TBD should we use the name here or the identifier?
	# def get_bake_scene_name(self):
	# 	return self.identifier

	#NOTE we should probably deprecate this in favor of iter_variants
	# this doesn't yield anything if there are no variants
	def iter_bake_scene_variants(self):
		prefix = self.name # self.get_bake_scene_name()
		if self.multi_variants:
			for variant in self.variant_collection:
				yield f'{prefix}.{variant.name}', variant


	def iter_variants(self):
		prefix = self.name # self.get_bake_scene_name()
		for variant in self.variant_collection:
			if self.multi_variants:
				yield f'{prefix}.{variant.name}', variant
			else:
				yield f'{prefix}', variant


	def iter_bake_scene_variant_names(self):
		prefix = self.name # self.get_bake_scene_name()
		if self.multi_variants:
			for variant in self.variant_collection:
				yield f'{prefix}.{variant.name}'
		else:
			yield prefix


#TEST
#BakeTarget.__annotations__['mirror_source'] = bpy.props.PointerProperty(name='Bake target used for mirror', type=BakeTarget)
# class BakeTargetReference(frame_property_group):
# 	target:					bpy.props.PointerProperty(name='bake target', type=BakeTarget)

class BakeTargetReference(frame_property_group):
	target:					bpy.props.IntProperty(name='Bake target identifier', default=-1)

class BakeGroup(frame_property_group):
	name: 					bpy.props.StringProperty(name="Group name", default='Untitled group')
	members:				bpy.props.CollectionProperty(type = BakeTargetReference)
	selected_member:		bpy.props.IntProperty(name = "Selected bake target", default = -1)

class BakeTargetMirrorEntry(frame_property_group):
	#Here I wanted to use PointerProperty but they don't really act as the name implies. See contribution note 7 for more details.
	primary: 				bpy.props.IntProperty(name='Primary bake target identifier', default=-1)
	secondary: 				bpy.props.IntProperty(name='Secondary bake target identifier', default=-1)


class HomeomorphicProperties(frame_property_group):

	### Bake targets ###

	#Note that we use -1 to indicate that nothing is selected for integer selections
	bake_target_collection: 			bpy.props.CollectionProperty(type = BakeTarget)
	selected_bake_target: 				bpy.props.IntProperty(name = "Selected bake target", default = -1)

	bake_target_mirror_collection: 		bpy.props.CollectionProperty(type = BakeTargetMirrorEntry)
	selected_bake_target_mirror: 		bpy.props.IntProperty(name = "Selected mirror entry", default = -1)

	bake_group_collection: 				bpy.props.CollectionProperty(type = BakeGroup)
	selected_bake_group: 				bpy.props.IntProperty(name = "Selected bake group", default = -1)

	source_object: 						bpy.props.StringProperty(name="Object name")

	### Atlas,textures, paint assist ###
	atlas_size: 						bpy.props.IntProperty(name="Atlas size", default = 4096)
	color_percentage:					bpy.props.FloatProperty(name="Atlas color region percentage", default = 25.0)

	painting_size:						bpy.props.IntProperty(name="Hand paint texture size", default = 1024)


	select_by_atlas_image:				bpy.props.PointerProperty(name='Match atlas', type=bpy.types.Image)

	def get_selected_bake_target(self):
		if self.selected_bake_target != -1:
			return self.bake_target_collection[self.selected_bake_target]

	def get_selected_bake_group(self):
		if self.selected_bake_group != -1:
			return self.bake_group_collection[self.selected_bake_group]

	def require_selected_bake_target(self):
		if candidate := self.get_selected_bake_target():
			return candidate
		else:
			raise Exception()	#TODO - proper exception

	def get_selected_mirror(self):
		if self.selected_bake_target_mirror != -1:
			return self.bake_target_mirror_collection[self.selected_bake_target_mirror]

	def require_selected_mirror(self):
		if candidate := self.get_selected_mirror():
			return candidate
		else:
			raise Exception()	#TODO - proper exception

	def get_bake_target_index(self, target):
		for index, bt in enumerate(self.bake_target_collection):
			if bt == target:	# note: We can't use identity comparison due to internal deferring in blender
				return index

		return -1

	def get_bake_target_by_identifier(self, identifier):
		for bt in self.bake_target_collection:
			if bt.identifier == identifier:
				return bt

	def require_bake_target_by_identifier(self, identifier):
		if candidate := self.get_bake_target_by_identifier(identifier):
			return candidate
		else:
			#TODO - proper exception
			raise Exception()
