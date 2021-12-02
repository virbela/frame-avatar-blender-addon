import bpy
import json
import os
from .mesh_utilities import get_uv_map_from_mesh, uv_transformation_calculator
import time
from . import utilities
from .utilities import hide_everything_from_render, get_named_image
from .baking import batch_bake


@utilities.register_class
class FRAME_OT_set_bake_mirror_primary(bpy.types.Operator):
	bl_label = "Set primary"
	bl_description = 'Set primary bake target of selected mirror entry'
	bl_idname = 'frame.set_bake_mirror_primary'

	#TODO - fix
	def execute(self, context):

		HT = context.scene.homeomorphictools
		et = HT.bake_target_collection[HT.selected_bake_target]
		tm = HT.bake_target_mirror_collection[HT.selected_bake_target_mirror]
		tm.primary = et.identifier

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_set_bake_mirror_secondary(bpy.types.Operator):
	bl_label = "Set secondary"
	bl_description = 'Set secondary bake target of selected mirror entry'
	bl_idname = 'frame.set_bake_mirror_secondary'

	#TODO - fix
	def execute(self, context):

		HT = context.scene.homeomorphictools
		et = HT.bake_target_collection[HT.selected_bake_target]
		tm = HT.bake_target_mirror_collection[HT.selected_bake_target_mirror]
		tm.secondary = et.identifier

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_add_bake_target_mirror(bpy.types.Operator):
	bl_label = "+"
	bl_description = 'Create new mirror entry'
	bl_idname = 'frame.add_bake_target_mirror'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		new = HT.bake_target_mirror_collection.add()


		last_id = len(HT.bake_target_mirror_collection) - 1
		HT.selected_bake_target_mirror = last_id

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_remove_bake_target_mirror(bpy.types.Operator):
	bl_label = "-"
	bl_description = 'Remove mirror entry'
	bl_idname = 'frame.remove_bake_target_mirror'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		HT.bake_target_mirror_collection.remove(HT.selected_bake_target_mirror)

		last_id = len(HT.bake_target_mirror_collection) - 1
		if last_id == -1:
			HT.selected_bake_target_mirror = -1
		else:
			HT.selected_bake_target_mirror = min(HT.selected_bake_target_mirror, last_id)

		return {'FINISHED'}




@utilities.register_class
class FRAME_OT_add_bake_target(bpy.types.Operator):
	bl_label = "+"
	bl_description = 'Create new bake target'
	bl_idname = 'frame.add_bake_target'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		new = HT.bake_target_collection.add()

		last_id = len(HT.bake_target_collection) - 1
		HT.selected_bake_target = last_id

		return {'FINISHED'}


@utilities.register_class
class FRAME_OT_remove_bake_target(bpy.types.Operator):
	bl_label = "-"
	bl_description = 'Remove selected bake target'
	bl_idname = 'frame.remove_bake_target'

	def execute(self, context):

		HT = context.scene.homeomorphictools
		HT.bake_target_collection.remove(HT.selected_bake_target)

		last_id = len(HT.bake_target_collection) - 1
		if last_id == -1:
			HT.selected_bake_target = -1
		else:
			HT.selected_bake_target = min(HT.selected_bake_target, last_id)

		return {'FINISHED'}


@utilities.register_class
class BAKETARGET_OT_my_op(bpy.types.Operator):
	bl_label = "Create bake targets"
	bl_idname = "targetcreate.mainoperator"

	def execute(self, context):
		time_start = time.time()
		# for i in range(10):
		# 	testitem = bpy.context.scene.my_list.add()
		# 	testitem.shapekey_name = "testing name"
		# 	#testitem.shapekey_index = 0

		scene = context.scene
		homeomorphictools = scene.homeomorphictools
		avatar_string = homeomorphictools.avatar_string
		collection_name = f"{avatar_string}_MorphSets"

		avatar_obj = bpy.data.objects[avatar_string]
		mesh_data = avatar_obj.data
		avatar_shapekeys = mesh_data.shape_keys.key_blocks

		# baketarget_material = f"{avatar_string}_BakeMaterial"

		# if bpy.data.materials.get(baketarget_material) == None:
		# 	bakematerial = bpy.data.materials.new(baketarget_material)
		# 	bakematerial.use_nodes = True

		# 	node_bsdf = bakematerial.node_tree.nodes.get('Principled BSDF')

		# 	node_rgb = bakematerial.node_tree.nodes.new('ShaderNodeRGB')
		# 	node_rgb.location = (-457, 267)

		# 	node_ao = bakematerial.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
		# 	node_ao.location = (-463, 39)

		# 	node_mix_rbg = bakematerial.node_tree.nodes.new('ShaderNodeMixRGB')
		# 	node_mix_rbg.location = (-208, 226)
		# 	node_mix_rbg.inputs['Fac'].default_value = 1
		# 	node_mix_rbg.blend_type = 'MULTIPLY'

		# 	bakematerial.node_tree.links.new(node_bsdf.inputs['Base Color'], node_mix_rbg.outputs[0])
		# 	bakematerial.node_tree.links.new(node_mix_rbg.inputs['Color2'], node_ao.outputs[0])
		# 	bakematerial.node_tree.links.new(node_mix_rbg.inputs['Color1'], node_rgb.outputs[0])

		# 	for node in bakematerial.node_tree.nodes:
		# 		node.select = False

		single_mesh_collection = bpy.data.collections.get(collection_name)
		if single_mesh_collection is None:
			single_mesh_collection = bpy.data.collections.new(collection_name) # create collection if not existing

			bpy.context.scene.collection.children.link(single_mesh_collection)
			bpy.context.scene.homeomorphictools.single_mesh = collection_name # add collection name to property group for later use

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


		#print("Executed in: %.4f sec" % (time.time() - time_start))
		return {'FINISHED'}

@utilities.register_class
class PACK_OT_my_op(bpy.types.Operator):
	bl_label = "Pack UVs"
	bl_idname = "pack.mainoperator"

	def execute(self, context):
		img_size = bpy.context.scene.homeomorphictools.imgsize_int
		packer_checkbox = bpy.context.scene.homeomorphictools.packer_bool
		relative_checkbox = bpy.context.scene.homeomorphictools.relative_bool
		packing_set = bpy.context.scene.homeomorphictools.single_mesh
		avatar_string = bpy.context.scene.homeomorphictools.avatar_string
		#uvset_string = bpy.context.scene.homeomorphictools.uvset_string

		avatar_obj = bpy.data.objects[avatar_string]
		collection_objs = bpy.data.collections[packing_set]

		red_collection = bpy.data.collections.new('red')
		green_collection = bpy.data.collections.new('green')
		blue_collection = bpy.data.collections.new('blue')

		bpy.context.scene.tool_settings.use_uv_select_sync = True


		avatar_obj.hide_viewport = True
		avatar_obj.hide_render = True
		avatar_obj.hide_set(True)
		avatar_obj.select_set(False)

		bpy.context.view_layer.objects.active = None


		for channel, target_collection in zip(('red', 'green', 'blue'), (red_collection, green_collection, blue_collection)):
			time_start = time.time()
			uvset_string = f'UV_map_{channel}'

			for obj in context.scene.objects:
				obj.select_set(False)



			# select all objects in collection
			for element in collection_objs.all_objects:

				if just_for_testing['lut'][element.name] != channel:
					continue

				target_collection.objects.link(element)

				element.select_set(True)
				bpy.context.view_layer.objects.active = element

				packing_uvset = element.data.uv_layers.get(uvset_string)

				if packing_uvset is None:
					packing_uvset = element.data.uv_layers.new(name=uvset_string)

				packing_uvset.active = True
				packing_uvset.active_render = True


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

@utilities.register_class
class BATCHBAKE_OT_my_op(bpy.types.Operator):
	bl_label = "Bake pass"
	bl_idname = "batch.mainoperator"

	def execute(self, context):
		#path = bpy.context.scene.homeomorphictools.path_string
		#color_checkbox = bpy.context.scene.homeomorphictools.color_bool
		#direct_color_checkbox = bpy.context.scene.homeomorphictools.color_bool
		direct_checkbox = bpy.context.scene.homeomorphictools.direct_bool
		#indirect_color_checkbox = bpy.context.scene.homeomorphictools.color_bool
		indirect_checkbox = bpy.context.scene.homeomorphictools.indirect_bool
		ao_checkbox = bpy.context.scene.homeomorphictools.ao_bool
		uvset_string = bpy.context.scene.homeomorphictools.uvset_string
		persistent_bool = bpy.context.scene.homeomorphictools.persistent_bool
		avatar_string = bpy.context.scene.homeomorphictools.avatar_string

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


		img_size = bpy.context.scene.homeomorphictools.imgsize_int
		tex_atlas = f"{avatar_string}_atlas"
		atlas = get_named_image(tex_atlas, size=(img_size, img_size), size_mandatory=True, auto_create=True)



		hide_everything_from_render()

		#bpy.context.view_layer.objects.active = None

		#bpy.context.object.data.uv_layers['UVMap'].active = True

		for bake_object in bpy.data.collections[collection_name].objects:

			#set assigned UVMap to active for every iteration

			#view_items = bpy.context.view_layer.objects.keys()

			#print(dir(bpy.context.view_layer.objects))

			#print(bpy.context.view_layer.objects.selected)
			bpy.context.view_layer.objects.active = bake_object


			print("bake_object.name: ", bake_object.name)
			print("currently selected objects:", bpy.context.view_layer.objects.active)
			#bake_object.select_set(True)
			bake_object.select_set(True)

			#object_uvset = bake_object.data.uv_layers[uvset_string]
			object_uvset = bake_object.data.uv_layers[uvset_string]
			print('UV set', object_uvset, object_uvset.active)
			object_uvset.active = True
			#bake_object.hide_render = False
			bake_object.hide_render = False

			object_uvset.active_render = True


			batch_bake(bake_object, atlas, uvset_string)


			bake_object.hide_render = True
			bake_object.select_set(False)

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

		# #show UV editor and avatar_atlas
		# original_area = bpy.context.area.type
		# original_area_width = bpy.context.area.width
		# original_area_height = bpy.context.area.height
		# bpy.ops.screen.area_split()
		# bpy.context.area.type = 'IMAGE_EDITOR'

		# for area in bpy.context.screen.areas:
		# 	if area.type == 'IMAGE_EDITOR':
		# 		area.spaces.active.image = bpy.data.images[f"{avatar_string}_atlas"]

		return {'FINISHED'}

@utilities.register_class
class EXPORTGLTF_OT_my_op(bpy.types.Operator):
	bl_label = "Export"
	bl_idname = "exportgltf.mainoperator"

	def __init__(self):
		self.morphs = {}

	def execute(self, context):
		packing_set = bpy.context.scene.homeomorphictools.single_mesh
		avatar_string = bpy.context.scene.homeomorphictools.avatar_string

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






from .baking import create_bake_material
@utilities.register_class
class BATCHBAKE_OT_test_operator(bpy.types.Operator):
	bl_label = "Test feature"
	bl_idname = "batch.testoperator"

	def execute(self, context):
		import bmesh

		#Test making material
		create_bake_material('bakmaterial')

		# #Testing getting UV area

		#packing_set = bpy.context.scene.homeomorphictools.single_mesh
		#collection_objs = bpy.data.collections[packing_set]
		#uvset_string = bpy.context.scene.homeomorphictools.uvset_string

		# area_per_name = dict()
		# for element in collection_objs.all_objects:
		# 	print(element.name)
		# 	uv_map = element.data.uv_layers.get(uvset_string)

		# 	mesh = bmesh.new()
		# 	mesh.from_mesh(element.data)

		# 	uv_area = sum(face.calc_area() for face in mesh.faces)
		# 	area_per_name[element.name] = uv_area



		# bins = [
		# 	['red', 0.0, []],
		# 	['green', 0.0, []],
		# 	['blue', 0.0, []],
		# ]

		# target_map = dict()

		# for name, area in sorted(area_per_name.items(), reverse=True, key=lambda x: x[1]):
		# 	target_name, target_area, target_list = target_bin = min(bins, key=lambda x: x[1])

		# 	target_map[name] = target_name
		# 	target_list.append(name)
		# 	target_bin[1] += area

		# for target_name, target_area, target_list in bins:
		# 	print('BIN', target_name, target_area)
		# 	print('   ', target_list)

		# just_for_testing['bins'] = bins
		# just_for_testing['lut'] = target_map

		return {'FINISHED'}

