import bpy
from . import utilities
import enum
from .helpers import enum_descriptor

class missing_action(enum.Enum):
	FAIL = object()
	RETURN_NONE = object()


UV_ISLAND_MODES = enum_descriptor(

	#Icons: https://blenderartists.org/uploads/default/original/4X/7/a/6/7a6b22e5e0fa4d2108dddc58c84c8b3d5e36e0ee.png

	#Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
	#(identifier, 			name, 				description,
	#	icon, 				number),

	('UV_IM_COLOR',			'Color',			'This UV island will end up on the color segment of the atlas',
		'COLOR',			0),

	('UV_IM_MONOCHROME',	'Monochrome',		'This UV island will be channel packed to a gray scale segment of the atlas',
		'IMAGE_ZDEPTH',		1),

	('UV_IM_NIL',			'Nil UV island',	'This UV island will have zero area (unshaded)',
		'DOT',				2),

	('UV_IM_FROZEN',		'Frozen',			'This UV island will not be modified by the packer',
		'FREEZE',			3),
)



@utilities.register_class
class BakeTarget(bpy.types.PropertyGroup):

	object_name: 		bpy.props.StringProperty(name="Object name")
	shape_key_name: 	bpy.props.StringProperty(name="Shape key")

	uv_area_weight: 	bpy.props.FloatProperty(name="UV island area weight", default=1.0)

	variant_count:		bpy.props.IntProperty(name="Variant count", default=1)

	uv_mode:			bpy.props.EnumProperty(items=UV_ISLAND_MODES, name="UV island mode", default=0)


	@property
	def description(self):
		if self.object_name:
			if self.shape_key_name:
				return f'{self.object_name}.{self.shape_key_name}'
			else:
				return self.object_name
		else:
			return '(No object selected)'

	@property
	def short_description(self):
		if self.object_name:
			if self.shape_key_name:
				return f'{self.object_name}.{self.shape_key_name}'
			else:
				return self.object_name
		else:
			return '???'

	@property
	def identifier(self):
		if self.object_name:
			if self.shape_key_name:
				return f'{self.object_name}.{self.shape_key_name}'
			else:
				return self.object_name

@utilities.register_class
class BakeTargetMirrorEntry(bpy.types.PropertyGroup):

	primary: 		bpy.props.StringProperty(name='Primary bake target')
	secondary:		bpy.props.StringProperty(name='Secondary bake target')



@utilities.register_class
class HomeomorphicProperties(bpy.types.PropertyGroup):
	#shapekeys_bool : bpy.props.BoolProperty(name="Shape key data", description="Inherit shape key name from object", default=True, get=None, set=None)
	#meshdata_bool : bpy.props.BoolProperty(name="Mesh data", description="Inherit mesh data-block name from object", default=True, get=None, set=None)
	avatar_string : bpy.props.StringProperty(name="MorphSets")#, update=list_shapekeys) <- function for populating UIList with shapekeys and other parameters
	uvset_string : bpy.props.StringProperty(name="UV set")
	single_mesh : bpy.props.StringProperty(name="Singular collection", description="Single mesh collection")
	packer_bool : bpy.props.BoolProperty(name="UVPackmaster/default packer", description="Use UVPackmaster to pack UVs, uncheck to use default packer", default=True, get=None, set=None)

	imgsize_int : bpy.props.IntProperty(name="Bake image size", default=4096) # default 4k
	path_string : bpy.props.StringProperty(name="Filepath")
	relative_bool : bpy.props.BoolProperty(name="Average island scale", description="Average UV island scale", default=True, get=None, set=None)
	persistent_bool : bpy.props.BoolProperty(name="Clear image", description="Persistent bakes per pass", default=False)
	#color_bool : bpy.props.BoolProperty(name="Color pass", description="Albedo", default=True, get=None, set=None)
	direct_bool : bpy.props.BoolProperty(name="Direct pass", description="Direct lighting", default=True, get=None, set=None)
	indirect_bool : bpy.props.BoolProperty(name="Indirect pass", description="Indirect lighting", default=True, get=None, set=None)
	ao_bool : bpy.props.BoolProperty(name="Ambient Occlusion pass", description="Ambient lighting", default=True, get=None, set=None)
	#direct_color_bool : bpy.props.BoolProperty(name="Color pass", description="Albedo", default=True, get=None, set=None)
	#indirect_color_bool : bpy.props.BoolProperty(name="Color pass", description="Albedo", default=True, get=None, set=None)




	#Note that we use -1 to indicate that nothing is selected for integer selections
	bake_target_collection: bpy.props.CollectionProperty(type = BakeTarget)
	selected_bake_target: bpy.props.IntProperty(name = "Selected bake target", default = -1)

	bake_target_mirror_collection: bpy.props.CollectionProperty(type = BakeTargetMirrorEntry)
	selected_bake_target_mirror: bpy.props.IntProperty(name = "Selected mirror entry", default = -1)




	def get_properties_by_names(self, names, if_missing=missing_action.FAIL):
		'Takes list of names separated by space and yields the values of those members.'

		if if_missing is missing_action.FAIL:
			return (getattr(self, member) for member in names.split())
		elif if_missing is missing_action.RETURN_NONE:
			return (getattr(self, member, None) for member in names.split())
		else:
			raise ValueError(f'if_missing has unknown value')



# class ShapekeyTable(bpy.types.PropertyGroup): #ShapekeyProperties
# 	shapekey_name : bpy.props.StringProperty(name="Shape key", default="Shape key")
# 	uv_scale : bpy.props.FloatProperty(default=1.0)
# 	shapekey_index : bpy.props.IntProperty(default=0)


# class MESHNAME_PT_main_panel(bpy.types.Panel):
# 	bl_label = "Organize data"
# 	bl_idname = "MESHNAME_PT_main_panel"
# 	bl_space_type = 'VIEW_3D'
# 	bl_region_type = 'UI'
# 	bl_category = "Avatar"

# 	def draw(self, context):
# 		layout = self.layout
# 		scene = context.scene
# 		homeomorphictools = scene.homeomorphictools
# 		row = layout.row()
# 		#layout.label(text="")
# 		row.prop(homeomorphictools, "meshdata_bool")
# 		row.prop(homeomorphictools, "shapekeys_bool")
# 		layout.operator("meshnamed.mainoperator")

# class MY_UL_List(bpy.types.UIList):
# 	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
# 		# We could write some code to decide which icon to use here...
# 		custom_icon = 'SHAPEKEY_DATA'
# 		# Make sure your code supports all 3 layout types
# 		if self.layout_type in {'DEFAULT', 'COMPACT'}:
# 			layout.label(text=item.name, icon = custom_icon)

# 		elif self.layout_type in {'GRID'}:
# 			layout.alignment = 'CENTER'
# 			layout.label(text="", icon = custom_icon)
