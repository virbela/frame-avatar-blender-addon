import bpy
from collections import deque

from . import operations
from .base import frame_operator
from ..helpers import (
    set_rendering,
    set_selection,
    require_bake_scene,
    get_homeomorphic_tool_state 
)

# Introduction
class FRAME_OT_setup_bake_scene(frame_operator):
    bl_label = 			"Create Bake Scene"
    bl_idname = 		"frame.setup_bake_scene"
    bl_description = 	"Create bake scene"
    frame_operator = 	operations.setup_bake_scene

# Export 
class FRAME_OT_export(frame_operator):
    bl_label = 			"Export GLTF"
    bl_idname = 		"frame.export"
    bl_description = 	"Export avatar meshes and metadata"
    frame_operator = 	operations.export


# Bake Targets
class FRAME_OT_create_targets_from_selection(frame_operator):
    bl_label = 			"New bake targets from selected objects"
    bl_idname = 		"frame.create_targets_from_selection"
    bl_description = 	"Create shape key targets from all selected objects"
    frame_operator = 	operations.create_targets_from_selection

class FRAME_OT_validate_targets(frame_operator):
    bl_label = 			"Validate bake targets"
    bl_idname = 		"frame.validate_targets"
    bl_description = 	"Verify that all bake properties are correctly set"
    frame_operator = 	operations.validate_targets


# Work Meshes
class FRAME_OT_create_workmeshes_for_all_targets(frame_operator):
    bl_label = 			"New work meshes from all bake targets"
    bl_idname = 		"frame.create_workmeshes_for_all_targets"
    bl_description = 	"Create bake meshes for all bake targets"
    frame_operator = 	operations.create_workmeshes_for_all_targets

class FRAME_OT_create_workmeshes_for_selected_target(frame_operator):
    bl_label = 			"New work meshes from selected bake targets"
    bl_idname = 		"frame.create_workmeshes_for_selected_target"
    bl_description = 	"Create bake meshes for the selected bake targets"
    frame_operator = 	operations.create_workmeshes_for_selected_target

class FRAME_OT_update_selected_workmesh_all_shapekeys(frame_operator):
    bl_label = 			"Update selected"
    bl_idname = 		"frame.update_selected_workmesh_all_shapekeys"
    bl_description = 	"Update vertex position data for all workmeshes"
    frame_operator = 	operations.update_selected_workmesh_all_shapekeys

class FRAME_OT_update_selected_workmesh_active_shapekey(frame_operator):
    bl_label = 			"Update active shapekey"
    bl_idname = 		"frame.update_selected_workmesh_active_shapekey"
    bl_description = 	"Update vertex position data for the active shape key mesh"
    frame_operator = 	operations.update_selected_workmesh_active_shapekey

class FRAME_OT_update_selected_workmesh(frame_operator):
    bl_label = 			"Update selected work mesh"
    bl_idname = 		"frame.update_selected_workmesh"
    #TODO - bl_description
    frame_operator = 	operations.update_selected_workmesh

class FRAME_OT_update_all_workmeshes(frame_operator):
    bl_label = 			"Update all work meshes"
    bl_idname = 		"frame.update_all_workmeshes"
    #TODO - bl_description
    frame_operator = 	operations.update_all_workmeshes


# Texture Atlas
class FRAME_OT_auto_assign_atlas(frame_operator):
    bl_label = 			"Auto assign atlas/UV"
    bl_idname = 		"frame.auto_assign_atlas"
    bl_description = 	"Go through the bake targets and assign atlas texture and UV layer for all non frozen bake targets."
    frame_operator = 	operations.auto_assign_atlas

class FRAME_OT_pack_uv_islands(frame_operator):
    bl_label = 			"Pack UV islands"
    bl_idname = 		"frame.pack_uv_islands"
    bl_description = 	"Go through the bake targets and pack workmesh uvs into intermediate atlases"
    frame_operator = 	operations.pack_uv_islands


# Work Materials
class FRAME_OT_update_selected_material(frame_operator):
    bl_label = 			"Update selected material"
    bl_idname = 		"frame.update_selected_material"
    bl_description = 	"Update the work mesh material for the selected bake target"
    frame_operator = 	operations.update_selected_material

class FRAME_OT_update_all_materials(frame_operator):
    bl_label = 			"Update all materials"
    bl_idname = 		"frame.update_all_materials"
    bl_description = 	"Update work mesh materials for all bake targets"
    frame_operator = 	operations.update_all_materials

class FRAME_OT_switch_to_bake_material(frame_operator):
    bl_label =			"Show bake/paint material"
    bl_description = 	'Switch all bake objects to use the bake material'
    bl_idname = 		'frame.switch_to_bake_material'
    frame_operator = 	operations.switch_to_bake_material

class FRAME_OT_switch_to_preview_material(frame_operator):
    bl_label =			"Show preview material"
    bl_description = 	'Switch all bake objects to use the preview material'
    bl_idname = 		'frame.switch_to_preview_material'
    frame_operator = 	operations.switch_to_preview_material

class FRAME_OT_select_by_atlas(frame_operator):
    bl_label = 			"Select work meshes based on atlas"
    bl_idname = 		"frame.select_by_atlas"
    bl_description = 	"Select all work meshes in `Match atlas`"
    frame_operator = 	operations.select_by_atlas


# Baking
class FRAME_OT_bake_selected_bake_target(frame_operator):
    #TODO - if we support multiple targets in selection we should change to plural here
    bl_label = 			"Bake selected target"
    bl_idname = 		"frame.bake_selected_bake_target"
    bl_description = 	"Bake textures for the selected bake target"
    frame_operator = 	operations.bake_selected_bake_target

class FRAME_OT_bake_selected_workmeshes(frame_operator):
    #TODO - if we support multiple targets in selection we should change to plural here
    bl_label = 			"Bake selected work meshes"
    bl_idname = 		"frame.bake_selected_workmeshes"
    bl_description = 	"Bake textures for selected work meshes"
    frame_operator = 	operations.bake_selected_workmeshes

class FRAME_OT_bake_all(frame_operator):
    bl_label = 			"Bake all targets"
    bl_idname = 		"frame.bake_all"
    bl_description = 	"Bake textures for all targets and their variants"
    frame_operator = 	operations.bake_all_bake_targets


# Helpers
class FRAME_OT_synchronize_uv_to_vertices(frame_operator):
    bl_label = 			"Select mesh vertices based on UV selection"
    bl_idname = 		"frame.synchronize_uv_to_vertices"
    bl_description = 	"Sync selection state for mesh and uvs"
    frame_operator = 	operations.synchronize_uv_to_vertices

class FRAME_OT_select_objects_by_uv(frame_operator):
    bl_label = 			"Select objects based on UV selection"
    bl_idname = 		"frame.select_objects_by_uv"
    bl_description = 	"Select all objects in the active uv"
    frame_operator =	operations.select_objects_by_uv

class FRAME_OT_synchronize_visibility_to_render(frame_operator):
    bl_label = 			"Show to render only"
    bl_idname = 		"frame.synchronize_visibility_to_render"
    bl_description =	"Will only make objects that are going to be rendered visible in the viewlayer"
    frame_operator = 	operations.synchronize_visibility_to_render

class FRAME_OT_make_everything_visible(frame_operator):
    bl_label = 			"Show everything"
    bl_idname = 		"frame.make_everything_visible"
    bl_description =	"Will make everything in the baking viewlayer visible"
    frame_operator = 	operations.make_everything_visible

class FRAME_OT_reset_uv_transforms(frame_operator):
    bl_label = 			"Reset UV transforms"
    bl_idname = 		"frame.reset_uv_transforms"
    bl_description =	"Resets UV transform to reflect the source object"
    frame_operator = 	operations.reset_uv_transforms

class FRAME_OT_recalculate_normals(frame_operator):
    bl_label = 			"Recalculate normals on selected meshes"
    bl_idname = 		"frame.recalculate_normals"
    bl_description =	"Recalculates normals to combat artifacts"
    frame_operator = 	operations.recalculate_normals

class FRAME_OT_update_baking_scene(frame_operator):
    bl_label = 			"Update baking scene"
    bl_idname = 		"frame.update_baking_scene"
    bl_description = 	"Regenerate bake scene objects from bake targets"
    frame_operator = 	operations.update_bake_scene

class FRAME_OT_synchronize_mirrors(frame_operator):
    bl_label =			"Synchronize mirrors"
    bl_description = 	'Copy settings from all primary targets to secondary targets in the mirror list'
    bl_idname = 		'frame.synchronize_mirrors'
    frame_operator = 	operations.synchronize_mirrors


# Bake Targets UI List
class FRAME_OT_add_bake_target(frame_operator):
    bl_label =			"+"
    bl_description = 	'Create new bake target'
    bl_idname = 		'frame.add_bake_target'
    frame_operator = 	operations.bake_targets.add

class FRAME_OT_show_selected_bt(frame_operator):
    bl_label =			"Edit selected"
    bl_description = 	(
                            'Edit selected bake target.\n'
                            'Activates shape key is needed'
                        )
    bl_idname = 		'frame.show_selected_bt'
    frame_operator = 	operations.bake_targets.edit_selected

class FRAME_OT_remove_bake_target(frame_operator):
    bl_label = 			"-"
    bl_description = 	'Remove selected bake target'
    bl_idname = 		'frame.remove_bake_target'
    frame_operator = 	operations.bake_targets.remove

class FRAME_OT_add_bake_target_variant(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Add variant'
    bl_idname = 		'frame.add_bake_target_variant'
    frame_operator =	operations.bake_variants.add

class FRAME_OT_remove_bake_target_variant(frame_operator):
    bl_label =			"-"
    bl_description = 	'Remove mirror entry'
    bl_idname = 		'frame.remove_bake_target_variant'
    frame_operator = 	operations.bake_variants.remove

class FRAME_OT_create_bake_targets_from_shapekeys(frame_operator):
    bl_label = 			"Create bake targets"
    bl_description = 	'Creates bake targets based on a specific naming convention'
    bl_idname = 		'frame.create_bake_targets_from_shapekeys'
    frame_operator = 	operations.create_bake_targets_from_shapekeys

class FRAME_OT_set_bake_mirror_primary(frame_operator):
    bl_label = 			"Set primary"
    bl_description = 	'Set primary bake target of selected mirror entry'
    bl_idname = 		'frame.set_bake_mirror_primary'
    frame_operator = 	operations.bake_mirrors.set_primary

class FRAME_OT_set_bake_mirror_secondary(frame_operator):
    bl_label = 			"Set secondary"
    bl_description = 	'Set secondary bake target of selected mirror entry'
    bl_idname = 		'frame.set_bake_mirror_secondary'
    frame_operator = 	operations.bake_mirrors.set_secondary

class FRAME_OT_add_bake_target_mirror(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Create new mirror entry'
    bl_idname = 		'frame.add_bake_target_mirror'
    frame_operator = 	operations.bake_mirrors.add

class FRAME_OT_remove_bake_target_mirror(frame_operator):
    bl_label =			"-"
    bl_description = 	'Remove mirror entry'
    bl_idname = 		'frame.remove_bake_target_mirror'
    frame_operator = 	operations.bake_mirrors.remove


# Bake Group UI List
class FRAME_OT_add_bake_group(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Create new bake group'
    bl_idname = 		'frame.add_bake_group'
    frame_operator = 	operations.bake_groups.add

class FRAME_OT_remove_bake_group(frame_operator):
    bl_label =			"-"
    bl_description = 	'Remove selected bake group'
    bl_idname = 		'frame.remove_bake_group'
    frame_operator = 	operations.bake_groups.remove

class FRAME_OT_add_bake_group_member(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Add selected bake target to bake group'
    bl_idname = 		'frame.add_bake_group_member'
    frame_operator = 	operations.bake_groups.members.add

class FRAME_OT_remove_bake_group_member(frame_operator):
    bl_label =			"-"
    bl_description = 	'Remove selected member from bake group'
    bl_idname = 		'frame.remove_bake_group_member'
    frame_operator = 	operations.bake_groups.members.remove

# Effects

class FRAME_OT_remove_effect(frame_operator):
    bl_label = 			"-"
    bl_description = 	'Remove selected effect'
    bl_idname = 		'frame.remove_effect'
    frame_operator = 	operations.effects.remove

class FRAME_OT_add_effect(frame_operator):
    bl_label = 			"+"
    bl_description = 	'Add variant'
    bl_idname = 		'frame.add_effect'
    frame_operator =	operations.effects.add


# DEVMODE
class FRAME_OT_node_get_links(frame_operator):
    bl_label = 			"Copy links"
    bl_idname = 		"frame.create_node_script"
    bl_description =	"Enumerate links to stdout for programmtic replication"
    frame_operator = 	operations.devtools.get_node_links

class FRAME_OT_clear_bake_scene(frame_operator):
    bl_label = 			"Remove everything from bake scene"
    bl_idname = 		"frame.clear_bake_scene"
    bl_description =	"This is for internal development purposes and should not be seen in distribution"
    frame_operator = 	operations.clear_bake_scene

class FRAME_OT_clear_bake_targets(frame_operator):
    bl_label = 			"Remove all bake targets"
    bl_idname = 		"frame.clear_bake_targets"
    bl_description =	"This is for internal development purposes and should not be seen in distribution"
    frame_operator =	operations.clear_bake_targets

# TODO(ranjian0)
# Modal operator to allow for progress when baking all targets
# https://blender.stackexchange.com/questions/170386/how-to-run-code-after-baking-with-invoke-default-has-finished

class BakeTask:
    def __init__(self, id, view_layer, bake_target, variant):
        self.id = id 
        self.view_layer = view_layer
        self.bake_target = bake_target
        self.variant = variant

        self._bake_img = bake_target.atlas 

    def run(self):
        workmesh = self.variant.workmesh

        #TODO - we should take into account bake groups - maybe also move this out to a more generic function
        set_rendering(self.view_layer.objects, workmesh)
        set_selection(self.view_layer.objects, workmesh, synchronize_active=True, make_sure_active=True)

        # set active image in material
        material_nodes = workmesh.active_material.node_tree.nodes
        material_nodes.active = material_nodes['tex_target']

        # set active UV index to source UV Map (since we want this in the final atlas)
        uv_layers = workmesh.data.uv_layers
        uv_layers.active = uv_layers[self.bake_target.source_uv_map]

        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.bake.use_clear = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.view_settings.view_transform = 'Standard'
        return bpy.ops.object.bake('INVOKE_DEFAULT', type='DIFFUSE')

    def finished(self):
        return self._bake_img.is_dirty

class FRANE_OT_modal_bake_all_targets(bpy.types.Operator):
    bl_label =          "Task queue for baking all targets"
    bl_idname =         "frame.modal_bake_all"
    bl_description =    "Bake textures for all targets and their variants"

    _img = None
    _timer = None
    _bake_task = None
    _bake_queue = deque()

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # Timer event happens every 0.5 seconds
            if not self._bake_queue:
                # XXX All tasks finished
                self.finish(context)
                return {'FINISHED'}

            if self._bake_task.finished():
                self._bake_task = self._bake_queue.popleft()
                result = self._bake_task.run()
                if result != {'RUNNING_MODAL'}:
                    self.report({'WARNING'}, "Baking failed")
                    return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context: bpy.types.Context):
        if context.scene.render.engine != 'CYCLES':
            context.scene.render.engine = 'CYCLES'

        HT = get_homeomorphic_tool_state(context)
        bake_scene = require_bake_scene(context)
        view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one

        # create the tasks
        for idx, bake_target in enumerate(HT.bake_target_collection, start=1):
            for variant in bake_target.variant_collection:	
                self._bake_queue.append(BakeTask(idx, view_layer, bake_target, variant))


        self._bake_task = self._bake_queue.popleft()        
        result = self._bake_task.run()
        if result != {'RUNNING_MODAL'}:
            self.report({'WARNING'}, "Failed to start baking")
            return {'FINISHED'}

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self.report({'INFO'}, "Baking map cancelled")

    def finish(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        self.report({'INFO'}, "Baking map completed")
        #save_image() # <--- Call the function after baking
    

