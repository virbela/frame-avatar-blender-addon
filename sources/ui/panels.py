import bpy
from .. import utilities
from ..properties import *
from ..helpers import get_work_scene, pending_classes

import textwrap

def textlines(txt):
	return textwrap.dedent(txt).strip('\r\n\t ').split('\n')

class frame_panel(bpy.types.Panel):
	#contribution note 6B
	def __init_subclass__(cls):
		pending_classes.append(cls)


class FRAME_PT_workflow(frame_panel):
	bl_label = "Workflow"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			#TODO - this should point to our documentation for the workflow. This could point to a document that requires the artist to be logged in to that web service (like google docs as an example).
			#We may not want links that anyone can access since the workflow should be considered proprietary
			op = self.layout.operator('wm.url_open', text='Help')
			op.url = 'http://example.org/'

			self.layout.operator('frame.auto_assign_atlas')

			self.layout.operator('frame.pack_uv_islands')
			self.layout.operator('frame.update_baking_scene')
			self.layout.operator('frame.bake_all')

			helpers = self.layout.box()
			helpers.label(text='Extra utilities')
			helpers.operator('frame.bake_selected')



class FRAME_PT_painting(frame_panel):
	bl_label = "Texture painting"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			self.layout.prop(HT, 'painting_size')


class FRAME_PT_uv_packing(frame_panel):
	bl_label = "Texture atlas"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):
		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			self.layout.prop(HT, 'atlas_size')
			self.layout.prop(HT, 'color_percentage')
			h = int(HT.color_percentage * HT.atlas_size / 100)
			self.layout.label(text=f'Height in pixels: {h}')




class FRAME_PT_batch_bake_targets(frame_panel):
	bl_label = "Bake targets"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Avatar"

	def draw(self, context):

		if scene := get_work_scene(context):
			HT = scene.homeomorphictools

			self.layout.template_list('FRAME_UL_bake_targets', '', HT,  'bake_target_collection', HT, 'selected_bake_target')

			bake_target_actions = self.layout.row(align=True)
			bake_target_actions.operator('frame.add_bake_target')
			bake_target_actions.operator('frame.remove_bake_target')

			#TODO - divy up this into a few functions to make it less messy
			if HT.selected_bake_target != -1:
				et = HT.bake_target_collection[HT.selected_bake_target]
				self.layout.prop_search(et, "object_name", scene, "objects")

				if obj := bpy.data.objects.get(et.object_name):
					if shape_keys := obj.data.shape_keys:
						self.layout.prop_search(et, "shape_key_name", obj.data.shape_keys, "key_blocks")


				self.layout.prop(et, 'uv_area_weight')

				variants = self.layout.box()
				variants.prop(et, 'multi_variants')

				if et.multi_variants:
					variants.template_list('FRAME_UL_bake_variants', '', et, 'variant_collection', et, 'selected_variant')

					variant_actions = variants.row(align=True)
					variant_actions.operator('frame.add_bake_target_variant')
					variant_actions.operator('frame.remove_bake_target_variant')

					if et.selected_variant != -1:
						var = et.variant_collection[et.selected_variant]
						variants.prop_search(var, 'image', bpy.data, 'images')


				self.layout.prop(et, 'uv_mode')

				if et.uv_mode == 'UV_IM_FROZEN':
					self.layout.prop_search(et, 'atlas', bpy.data, 'images')
					if obj:
						self.layout.prop_search(et, 'uv_set', obj.data, 'uv_layers')
					else:
						self.layout.label(text=f"UV set: (No object)'")
				else:
					self.layout.label(text=f"Atlas: {et.atlas or '(not assigned)'}")
					self.layout.label(text=f"UV set: {et.uv_set or '(not assigned)'}")



			mirrors = self.layout.box()
			mirrors.label(text='Mirrored bake targets')
			mirrors.template_list('FRAME_UL_bake_target_mirrors', '', HT,  'bake_target_mirror_collection', HT, 'selected_bake_target_mirror')

			bake_target_actions = mirrors.row(align=True)
			bake_target_actions.operator('frame.add_bake_target_mirror')
			bake_target_actions.operator('frame.remove_bake_target_mirror')

			if HT.selected_bake_target_mirror != -1:
				tm = HT.bake_target_mirror_collection[HT.selected_bake_target_mirror]
				row = mirrors.row()
				row.operator('frame.set_bake_mirror_primary')
				row.operator('frame.set_bake_mirror_secondary')


			advanced = self.layout.box()
			advanced.label(text='Create from shapekeys')
			advanced.prop_search(HT, 'source_object', scene, 'objects')
			advanced.operator('frame.create_bake_targets_from_shapekeys')