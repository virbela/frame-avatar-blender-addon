bl_info = {
	"name": "Homeomorphic avatar creator",
	"description": "Homeomorphic avatar creation tools",
	"author": "Martin Petersson",
	"version": (0, 0, 1),
	"blender": (2, 92, 2),
	"location": "View3D",
	"warning": "",
	"wiki_url": "",
	"category": "Avatars"}
#dependencies: UVPackmaster 2.5.8

import bpy
from mathutils import Vector
from math import atan2, pi
import bmesh
from dataclasses import dataclass, asdict
import json
import os

from .mesh_utilities import get_uv_map_from_mesh, uv_transformation_calculator

import time

def print_to_editor(string, outputname):
	text_input = str(string)

	textdata = bpy.data.texts

	if textdata.get(outputname) == None:
		#textdata.new(f'.{outputname}') # hidden in text editor
		textdata.new(outputname) # not hidden

	textdata[outputname].from_string(string) # overwrite existing


@dataclass(order=True)
class MorphSet:
	Morphs: dict

@dataclass(order=True)
class transform:
	scale: float
	rotation: float
	translation: tuple

@dataclass(order=True)
class basis_object:
	name: str
	collection: str

	uv_verts: list
	scale: float
	centroid: tuple


""" Add feature baking objects in isolation """

def batch_bake(named_obj):
	img_size = bpy.context.scene.homomorphictools.imgsize_int
	avatar_string = bpy.context.scene.homomorphictools.avatar_string
	color_checkbox = bpy.context.scene.homomorphictools.color_bool
	#direct_checkbox = bpy.context.scene.homomorphictools.direct_bool
	#indirect_checkbox = bpy.context.scene.homomorphictools.indirect_bool
	ao_checkbox = bpy.context.scene.homomorphictools.ao_bool
	uvset_string = bpy.context.scene.homomorphictools.uvset_string

	bpy.context.view_layer.objects.active = bpy.data.objects[named_obj]
	obj_selection = bpy.context.active_object

	tex_atlas = f"{avatar_string}_atlas"

	if color_checkbox == True:
		bpy.context.scene.cycles.bake_type = 'DIFFUSE'
		bpy.context.scene.render.bake.use_pass_direct = False
		bpy.context.scene.render.bake.use_pass_indirect = False
		bpy.context.scene.render.bake.use_pass_color = True

		if bpy.data.images.get(tex_atlas) != None:
			img = bpy.data.images.get(tex_atlas)
			if img_size != img.size[0]:
				bpy.data.images.remove(img)
				img = bpy.data.images.new(tex_atlas, img_size, img_size)
				img.generated_color[0] = 0.788
				img.generated_color[1] = 0.788
				img.generated_color[2] = 0.788
				img.generated_color[3] = 1
		else:
			img = bpy.data.images.new(tex_atlas, img_size, img_size)
			img.generated_color[0] = 0.788
			img.generated_color[1] = 0.788
			img.generated_color[2] = 0.788
			img.generated_color[3] = 1


		active_mat = bpy.context.active_object.active_material

		if active_mat != None:
			for mat in obj_selection.data.materials:
				if mat == active_mat:
					mat.use_nodes = True
					nodes = mat.node_tree.nodes

					for current_node in nodes:
						current_node.select = False

					if mat.node_tree.nodes.get('BakeNode') == None:
						texture_node = nodes.new('ShaderNodeTexImage')
						texture_node.name = 'BakeNode'
						texture_node.location = (0, 688)
						texture_node.select = True
						texture_node.image = bpy.data.images[tex_atlas]
					else:
						texture_node = mat.node_tree.nodes.get('BakeNode')
						texture_node.image = bpy.data.images[tex_atlas]
					if bpy.data.images[tex_atlas] == None:
						print("no image found!")
						#fix error with no image found in active material if removed
						continue

					# create uv node and connect it to bake target texture node
					# assign the UV set from the "uvset_string" in PropertyGroup

					if mat.node_tree.nodes.get('UVBakeNode') == None:
						uv_node = nodes.new('ShaderNodeUVMap')
						uv_node.name = 'UVBakeNode'
						uv_node.location = (-196, 540)
						uv_node.uv_map = uvset_string
						mat.node_tree.links.new(texture_node.inputs[0], uv_node.outputs[0])
					else:
						uv_node = mat.node_tree.nodes.get('UVBakeNode')
						uv_node.uv_map = uvset_string
						texture_node.image = bpy.data.images.get(tex_atlas)

					nodes.active = None
					nodes.active = texture_node
		else:
			print("ERROR! No material assigned to object!") #specify which object has a missing material

		bpy.context.view_layer.objects.active = bpy.data.objects[named_obj]
		bpy.context.view_layer.objects[named_obj].select_set(True)

		img = bpy.data.images[tex_atlas]
		img.file_format = 'PNG'
		img.filepath_raw = f"//{tex_atlas}.png"

		bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')

		img.save()

	"""
		for mat in obj.data.materials:
			for n in mat.node_tree.nodes:
				if n.name == 'BakeNode':
					mat.node_tree.nodes.remove(n)
	"""

	"""
	import bpy

	wm = bpy.context.window_manager

	# progress from [0 - 1000]
	tot = 1000
	wm.progress_begin(0, tot)

	for i in range(tot):
		wm.progress_update(i)
	wm.progress_end()
	"""
	return



""" PROPERTIES """

class HomomorphicProperties(bpy.types.PropertyGroup):
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
	color_bool : bpy.props.BoolProperty(name="Color pass", description="Albedo", default=True, get=None, set=None)
	direct_bool : bpy.props.BoolProperty(name="Direct pass", description="Direct lighting", default=True, get=None, set=None)
	indirect_bool : bpy.props.BoolProperty(name="Indirect pass", description="Indirect lighting", default=True, get=None, set=None)
	ao_bool : bpy.props.BoolProperty(name="Ambient Occlusion pass", description="Ambient lighting", default=True, get=None, set=None)
	#direct_color_bool : bpy.props.BoolProperty(name="Color pass", description="Albedo", default=True, get=None, set=None)
	#indirect_color_bool : bpy.props.BoolProperty(name="Color pass", description="Albedo", default=True, get=None, set=None)

"""
class ShapekeyTable(bpy.types.PropertyGroup): #ShapekeyProperties
	shapekey_name : bpy.props.StringProperty(name="Shape key", default="Shape key")
	uv_scale : bpy.props.FloatProperty(default=1.0)
	shapekey_index : bpy.props.IntProperty(default=0)
"""

""" UI PANELS """

"""
class MESHNAME_PT_main_panel(bpy.types.Panel):
	bl_label = "Organize data"
	bl_idname = "MESHNAME_PT_main_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		homomorphictools = scene.homomorphictools
		row = layout.row()
		#layout.label(text="")
		row.prop(homomorphictools, "meshdata_bool")
		row.prop(homomorphictools, "shapekeys_bool")
		layout.operator("meshnamed.mainoperator")
"""
"""
class MY_UL_List(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		# We could write some code to decide which icon to use here...
		custom_icon = 'SHAPEKEY_DATA'
		# Make sure your code supports all 3 layout types
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			layout.label(text=item.name, icon = custom_icon)

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label(text="", icon = custom_icon)
"""

class BAKETARGET_PT_main_panel(bpy.types.Panel):
	bl_label = "Create bake targets"
	bl_idname = "BAKETARGETS_PT_main_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		homomorphictools = scene.homomorphictools

		layout.prop_search(homomorphictools, "avatar_string", scene, "objects")
		#row = layout.row()
		#row.template_list("MY_UL_List", "The_List", scene, "my_list", scene, "list_index")
		layout.operator("targetcreate.mainoperator")

class PACK_PT_main_panel(bpy.types.Panel):
	bl_label = "Packing"
	bl_idname = "PACKING_PT_main_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		layout = self.layout
		scene = context.scene

		homomorphictools = scene.homomorphictools

		layout.prop(homomorphictools, "imgsize_int")

		layout.prop(homomorphictools, "uvset_string")
		layout.prop(homomorphictools, "relative_bool")
		layout.prop(homomorphictools, "packer_bool")
		layout.operator("pack.mainoperator")

class BATCHBAKE_PT_main_panel(bpy.types.Panel):
	bl_label = "Batch bake"
	bl_idname = "BATCHBAKING_PT_main_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		homomorphictools = scene.homomorphictools

		#layout.prop(homomorphictools, "path_string")
		layout.prop(homomorphictools, "color_bool")
		#layout.prop(homomorphictools, "direct_bool")
		#layout.prop(homomorphictools, "indirect_bool")
		layout.prop(homomorphictools, "ao_bool")
		layout.prop(homomorphictools, "persistent_bool")
		layout.operator("batch.mainoperator")

class EXPORTGLTF_PT_main_panel(bpy.types.Panel):
	bl_label = "Export glTF"
	bl_idname = "EXPORTGLTFS_PT_main_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		homomorphictools = scene.homomorphictools

		layout.operator("exportgltf.mainoperator")


""" OPERATORS """
"""
class MESHNAME_OT_my_op(bpy.types.Operator):
	bl_label = "Object name to mesh data"
	bl_idname = "meshnamed.mainoperator"

	def execute(self, context):
		meshdata_checkbox = bpy.context.scene.homomorphictools.meshdata_bool
		shapekeys_checkbox = bpy.context.scene.homomorphictools.shapekeys_bool

		for obj in bpy.context.selected_objects:
			if (obj.type == 'MESH'):
				#print("name of object selected: ", obj.name)
				if meshdata_checkbox == True:
					obj.data.name = obj.name #+ '_MeshData'
				if shapekeys_checkbox == True:
					#bpy.context.object.data.shape_keys.name
					obj.data.shape_keys.name = obj.name #+ '_ShapeKeys'

		return {'FINISHED'}
"""
class BAKETARGET_OT_my_op(bpy.types.Operator):
	bl_label = "Create bake targets"
	bl_idname = "targetcreate.mainoperator"

	def execute(self, context):
		time_start = time.time()
		"""
		for i in range(10):
			testitem = bpy.context.scene.my_list.add()
			testitem.shapekey_name = "testing name"
			#testitem.shapekey_index = 0
		"""

		""" Below changed use Git """
		scene = context.scene
		homomorphictools = scene.homomorphictools
		avatar_string = homomorphictools.avatar_string

		collection_name = f"{avatar_string}_MorphSets"
		""" Above changed use Git """

		avatar_obj = bpy.data.objects[avatar_string]
		mesh_data = avatar_obj.data
		avatar_shapekeys = bpy.data.meshes[mesh_data.name].shape_keys.key_blocks

		baketarget_material = f"{avatar_string}_BakeMaterial"

		if bpy.data.materials.get(baketarget_material) == None:
			bakematerial = bpy.data.materials.new(baketarget_material)
			bakematerial.use_nodes = True

			node_bsdf = bakematerial.node_tree.nodes.get('Principled BSDF')

			node_rgb = bakematerial.node_tree.nodes.new('ShaderNodeRGB')
			node_rgb.location = (-457, 267)

			node_ao = bakematerial.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
			node_ao.location = (-463, 39)

			node_mix_rbg = bakematerial.node_tree.nodes.new('ShaderNodeMixRGB')
			node_mix_rbg.location = (-208, 226)
			node_mix_rbg.inputs['Fac'].default_value = 1
			node_mix_rbg.blend_type = 'MULTIPLY'

			bakematerial.node_tree.links.new(node_bsdf.inputs['Base Color'], node_mix_rbg.outputs[0])
			bakematerial.node_tree.links.new(node_mix_rbg.inputs['Color2'], node_ao.outputs[0])
			bakematerial.node_tree.links.new(node_mix_rbg.inputs['Color1'], node_rgb.outputs[0])

			for node in bakematerial.node_tree.nodes:
				node.select = False

		single_mesh_collection = bpy.data.collections.get(collection_name)
		if single_mesh_collection is None:
			single_mesh_collection = bpy.data.collections.new(collection_name) # create collection if not existing

			bpy.context.scene.collection.children.link(single_mesh_collection)
			bpy.context.scene.homomorphictools.single_mesh = collection_name # add collection name to property group for later use

		if avatar_string != "":

			# make singular meshes and name by shape key
			for shape in avatar_shapekeys:
				#if shape.name != "Basis":

				if '__' in str(shape.name):
					continue
				else:
					copy_obj = avatar_obj.copy()
					copy_obj.data = avatar_obj.data.copy()
					copy_obj.active_material = bpy.data.materials[baketarget_material]
					#copy_obj.data.materials.clear()

					#shapekey_to_mesh = bpy.data.objects.new(f'{avatar_string}_{shape.name}', avatar_obj.data)

					copy_obj.name = f'{avatar_string}_{shape.name}'
					#copy_obj.name = f'{shape.name}'
					copy_obj.data.name = copy_obj.name
					bpy.data.collections[single_mesh_collection.name].objects.link(copy_obj)



		# make active object
		#bpy.context.view_layer.objects.active = bpy.data.objects[copy_obj.name]
		bpy.context.view_layer.objects.active = None

		avatar_obj.hide_set(True)
		avatar_obj.select_set(False)

		#collection_avatar_obj = bpy.data.collections[avatar_string]
		bpy.data.objects[avatar_string].hide_viewport = True
		bpy.data.objects[avatar_string].hide_render = True


		morphset_shapekeys = avatar_shapekeys

		shapekeys_list = []

		for shape in morphset_shapekeys.items():
			shapekeys_list.append(shape[0])

		for i in bpy.data.collections[collection_name].objects:
			#obj_name_keyshape = i.name

			if current_object := bpy.data.objects.get(i.name):
				bpy.context.view_layer.objects.active = current_object

				for current_shape in shapekeys_list:

					if i.name != f"{avatar_string}_{current_shape}":
						bpy.context.active_object.shape_key_remove(bpy.data.meshes[i.name].shape_keys.key_blocks[current_shape])
			# remove last key or delete since it changes the shading?
			#bpy.context.active_object.shape_key_clear()

		bpy.context.view_layer.objects.active = None


		print("Executed in: %.4f sec" % (time.time() - time_start))
		return {'FINISHED'}


class PACK_OT_my_op(bpy.types.Operator):
	bl_label = "Pack UVs"
	bl_idname = "pack.mainoperator"

	def execute(self, context):
		time_start = time.time()
		img_size = bpy.context.scene.homomorphictools.imgsize_int
		packer_checkbox = bpy.context.scene.homomorphictools.packer_bool
		relative_checkbox = bpy.context.scene.homomorphictools.relative_bool
		packing_set = bpy.context.scene.homomorphictools.single_mesh
		avatar_string = bpy.context.scene.homomorphictools.avatar_string
		uvset_string = bpy.context.scene.homomorphictools.uvset_string

		avatar_obj = bpy.data.objects[avatar_string]
		collection_objs = bpy.data.collections[packing_set]

		bpy.context.scene.tool_settings.use_uv_select_sync = True


		for obj in context.scene.objects:
			obj.select_set(False)

		avatar_obj.hide_set(True)
		avatar_obj.select_set(False)

		bpy.data.objects[avatar_string].hide_viewport = True
		bpy.data.objects[avatar_string].hide_render = True

		bpy.context.view_layer.objects.active = None

		# select all objects in collection
		for element in collection_objs.all_objects:

			element.select_set(True)
			bpy.context.view_layer.objects.active = element

			if element.data.uv_layers.get(uvset_string) == None:
				if element.name != avatar_obj.name: #                                                                                  <- REMOVE?
					if uvset_string != "":
						packing_uvset = bpy.data.objects[element.name].data.uv_layers[uvset_string]
					else:
						packing_uvset = bpy.data.objects[element.name].data.uv_layers.get('UVMap')

					packing_uvset.active = True
					packing_uvset.active_render = True
			else:
				try:
					if element.name != avatar_obj.name: #                                                                              <- REMOVE?
						bpy.data.objects[element.name].data.uv_layers.active = bpy.data.objects[element.name].data.uv_layers.get(uvset_string)
						packing_uvset = bpy.data.objects[element.name].data.uv_layers[uvset_string]
						packing_uvset.active = True
						packing_uvset.active_render = True
				except:
					print("Getting UV layers not working!!")


		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.uv.select_all(action='SELECT')

		#check if overlapping first and run this, alternatively pack using the standard packer and use a small margin like 0.001:
		#print(bpy.ops.uvpackmaster2.uv_overlap_check())

		if relative_checkbox:
			bpy.ops.uv.average_islands_scale()

		if packer_checkbox:
			bpy.ops.uvpackmaster2.split_overlapping_islands()

		# Calculate UV margin
		uv_margin_extra_pixels = 50
		bake_margin_pixels = bpy.context.scene.render.bake.margin
		uv_margin_pixels = bake_margin_pixels + uv_margin_extra_pixels
		uv_margin = uv_margin_pixels / img_size

		# Pack UV islands
		if packer_checkbox:
			bpy.context.scene.uvp2_props.margin = uv_margin
			#bpy.context.scene.uvp2_props.precision = 2000# max(2048, img_size)
			bpy.ops.uvpackmaster2.uv_pack() # pack uvs
		else:
			bpy.ops.uv.pack_islands(margin=uv_margin)

		# Deselect everything
		for element in collection_objs.all_objects:
			bpy.data.objects[element.name_full].select_set(False)
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		print("Executed in: %.4f sec" % (time.time() - time_start))
		return {'FINISHED'}

def hide_everything_from_render():
	for obj in bpy.data.objects:
		obj.hide_render = True


class BATCHBAKE_OT_my_op(bpy.types.Operator):
	bl_label = "Bake pass"
	bl_idname = "batch.mainoperator"

	def execute(self, context):
		#path = bpy.context.scene.homomorphictools.path_string
		color_checkbox = bpy.context.scene.homomorphictools.color_bool
		#direct_color_checkbox = bpy.context.scene.homomorphictools.color_bool
		direct_checkbox = bpy.context.scene.homomorphictools.direct_bool
		#indirect_color_checkbox = bpy.context.scene.homomorphictools.color_bool
		indirect_checkbox = bpy.context.scene.homomorphictools.indirect_bool
		ao_checkbox = bpy.context.scene.homomorphictools.ao_bool
		uvset_string = bpy.context.scene.homomorphictools.uvset_string
		persistent_bool = bpy.context.scene.homomorphictools.persistent_bool
		avatar_string = bpy.context.scene.homomorphictools.avatar_string

		avatar_obj = bpy.data.objects[avatar_string]

		collection_name = f"{avatar_string}_MorphSets"

		render_settings = bpy.context.scene
		render_settings.render.engine = 'CYCLES'
		render_settings.render.bake.margin = 2
		render_settings.cycles.samples = 8

		if persistent_bool == True:
			bpy.context.scene.render.bake.use_clear = True
		elif persistent_bool == False:
			bpy.context.scene.render.bake.use_clear = False


		hide_everything_from_render()

		bpy.context.view_layer.objects.active = None

		#bpy.context.object.data.uv_layers['UVMap'].active = True

		for bake_object in bpy.data.collections[collection_name].objects:

			#set assigned UVMap to active for every iteration
			bpy.context.view_layer.objects.active = bpy.data.objects[bake_object.name]

			print("bake_object.name: ", bake_object.name)
			print("currently selected objects:", bpy.context.view_layer.objects.active)
			#bpy.data.objects[bake_object.name].select_set(True)
			bake_object.select_set(True)

			#object_uvset = bpy.data.objects[bake_object.name].data.uv_layers[uvset_string]
			object_uvset = bake_object.data.uv_layers[uvset_string]
			object_uvset.active = True
			#bpy.data.objects[bake_object.name].hide_render = False
			bake_object.hide_render = False

			object_uvset.active_render = True


			batch_bake(bake_object.name)


			# bpy.data.objects[bake_object.name].hide_render = True
			# bpy.data.objects[bake_object.name].select_set(False)

			bake_object.name.hide_render = True
			bake_object.name.select_set(False)

		for obj in bpy.data.collections[collection_name].objects:
			obj.hide_render = False


		# create export material

		export_material = f"{avatar_string}_ExportMaterial"

		if bpy.data.materials.get(export_material) == None:
			exportmaterial = bpy.data.materials.new(export_material)
			exportmaterial.use_nodes = True

			node_output = exportmaterial.node_tree.nodes.get('Material Output')

			node_bsdf = exportmaterial.node_tree.nodes.get('Principled BSDF')
			exportmaterial.node_tree.nodes.remove(node_bsdf)

			node_bg = exportmaterial.node_tree.nodes.new('ShaderNodeBackground')
			node_bg.location = (111, 260)

			node_tex = exportmaterial.node_tree.nodes.new('ShaderNodeTexImage')
			node_tex.image = bpy.data.images[f"{avatar_string}_atlas"]

			node_tex.location = (-185, 260)

			node_uv = exportmaterial.node_tree.nodes.new('ShaderNodeUVMap')
			bpy.data.materials["Avatar_ExportMaterial"].node_tree.nodes["UV Map"].uv_map = "UVMap"
			node_uv.location = (-375, 50)

			exportmaterial.node_tree.links.new(node_output.inputs['Surface'], node_bg.outputs['Background'])
			exportmaterial.node_tree.links.new(node_bg.inputs['Color'], node_tex.outputs['Color'])
			exportmaterial.node_tree.links.new(node_tex.inputs['Vector'], node_uv.outputs['UV'])

		avatar_obj.active_material = bpy.data.materials[export_material]
		print("active material: ", avatar_obj.active_material)

		#show UV editor and avatar_atlas
		original_area = bpy.context.area.type
		original_area_width = bpy.context.area.width
		original_area_height = bpy.context.area.height
		bpy.ops.screen.area_split()
		bpy.context.area.type = 'IMAGE_EDITOR'

		for area in bpy.context.screen.areas:
			if area.type == 'IMAGE_EDITOR':
				area.spaces.active.image = bpy.data.images[f"{avatar_string}_atlas"]

		return {'FINISHED'}



class EXPORTGLTF_OT_my_op(bpy.types.Operator):
	bl_label = "Export"
	bl_idname = "exportgltf.mainoperator"

	def __init__(self):
		self.morphs = {}

	def execute(self, context):
		packing_set = bpy.context.scene.homomorphictools.single_mesh
		avatar_string = bpy.context.scene.homomorphictools.avatar_string

		#collection_name = f"{avatar_string}_MorphSets"

		#avatar_obj = bpy.data.objects[avatar_string]


		if avatar_string != "":
			avatar_obj = bpy.data.objects[avatar_string] # should be referencing the object directly instead of by name!
			mesh_data = avatar_obj.data
			#Note - We are skipping the first key here and since base object is the first one this should not be a problem
			avatar_shapekeys = bpy.data.meshes[mesh_data.name].shape_keys.key_blocks[1:]

		# CHANGE LAYER VISIBILITY AND SELECT MORPHSET OBJECT
		for obj in context.scene.objects:
			obj.select_set(False)
			#bpy.ops.outliner.hide()

		# proper use of avatar_obj and avatar_string?
		avatar_obj.hide_set(False)
		avatar_obj.hide_viewport = False
		avatar_obj.select_set(True)


		""" CREATE METADATA """

		uv_transform_extra_data = list()		#This is used for the actual gtlf export
		uv_transform_map = dict()				#This is used temporarily so that we can fetch the corresponding UV transform

		#Acquite UV map from original avatar and prepare uv transformation calculator
		uvtc = uv_transformation_calculator(get_uv_map_from_mesh(avatar_obj))

		for name, item in bpy.data.collections[packing_set].all_objects.items():

			#Acquire the UV map from the mesh and calculate transform from reference map
			stripped_shapekey_name = name[len(f"{avatar_string}_"):]	#This assumes the name begins with the pattern, if the collection is modified it would cause weird names, maybe even an empty name in worst case
			print(f'Getting transform for: {name}')
			uv_transform_map[stripped_shapekey_name] = uvtc.calculate_transform(get_uv_map_from_mesh(item))

		# loop shapekeys here for '__'
		for shape in avatar_shapekeys:
			shape_name = str(shape.name)

			#Strip __None if present
			if shape_name.endswith('__None'):
				shape_name = shape_name[:-6]

			uv_transform_extra_data.append((shape.name, dict(UVTransform = uv_transform_map.get(shape_name))))

		morphsets_dict = {f"MorphSets_{avatar_string}": uv_transform_extra_data}
		export_json = json.dumps(morphsets_dict, sort_keys=False, indent=2)
		print_to_editor(export_json, 'extras_dump')


		filepath = bpy.data.filepath
		directory = os.path.dirname(filepath)

		outputfile = os.path.join(directory , f"{avatar_string}.gltf")
		outputfile_glb = os.path.join(directory , f"{avatar_string}.glb")

		bpy.ops.export_scene.gltf(filepath=outputfile, export_format='GLTF_EMBEDDED', export_texcoords=True, export_normals=True, use_selection=True, export_extras=False, export_morph=True, will_save_settings=True)

		with open(outputfile, 'r') as openfile:
			json_data = json.load(openfile)

		json_data["extras"] = morphsets_dict

		# save modified GLTF
		with open(outputfile, 'w') as exportfile:
			json.dump(json_data, exportfile, indent=4)

		# open modified GLTF, re-export as GLB
		avatar_obj.select_set(False)

		bpy.ops.import_scene.gltf(filepath=outputfile)
		imported_gltf = bpy.context.active_object
		imported_gltf.select_set(True)

		bpy.ops.export_scene.gltf(filepath=outputfile_glb, export_format='GLB', export_texcoords=True, export_normals=True, use_selection=True, export_extras=True, export_morph=True, will_save_settings=True)
		print(bpy.context.active_object)
		bpy.ops.object.delete()

		return {'FINISHED'}


""" Registering classes """

classes = [HomomorphicProperties,
		   #ShapekeyTable,
		   #MESHNAME_PT_main_panel,
		   #MY_UL_List,
		   BAKETARGET_PT_main_panel,
		   PACK_PT_main_panel,
		   BATCHBAKE_PT_main_panel,
		   EXPORTGLTF_PT_main_panel,
		   #MESHNAME_OT_my_op,
		   BAKETARGET_OT_my_op,
		   PACK_OT_my_op,
		   BATCHBAKE_OT_my_op,
		   EXPORTGLTF_OT_my_op]
		   #MY_UL_List,

def register():
	#bpy.types.Scene.shapekey_uvprops = CollectionProperty(type=ShapekeyProperties)
	#bpy.utils.register_class(MY_UL_List)
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.homomorphictools = bpy.props.PointerProperty(type=HomomorphicProperties)
	#bpy.types.Scene.my_list = bpy.props.CollectionProperty(type=ShapekeyTable)

	#bpy.types.Scene.list_index = bpy.props.IntProperty(name="Shape key index", default=0)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.homomorphictools
	#del bpy.types.Scene.ShapekeyTable # dunno if correct, delete this line if not. also delete from classes if incorrect.

if __name__ == "__main__":
	register()
