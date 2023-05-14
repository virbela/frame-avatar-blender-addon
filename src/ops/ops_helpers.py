import bpy
import bmesh
from bpy.types import Operator, Context, Object

from .base import FabaOperator
from ..utils.constants import MIRROR_TYPE
from ..utils.helpers import require_bake_scene, set_selection
from ..props import BakeTarget, HomeomorphicProperties
from .common import set_uv_map, copy_object, copy_collection, transfer_variant

def synchronize_uv_to_vertices(operator: Operator, context: Context, ht: HomeomorphicProperties):
    mesh = bmesh.from_edit_mesh(context.active_object.data)
    uv_layer = mesh.loops.layers.uv.active

    for vert in mesh.verts:
        vert.select_set(False)

    for vert in mesh.verts:
        for loop in vert.link_loops:
            uv = loop[uv_layer]
            if uv.select:
                vert.select_set(True)
                break

    bmesh.update_edit_mesh(context.active_object.data)


def select_objects_by_uv(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene()
    to_select = list()
    for obj in bake_scene.objects:
        mesh = bmesh.new()
        mesh.from_mesh(obj.data)
        uv_layer_index = mesh.loops.layers.uv.active

        def check_candidate_object():
            for face in mesh.faces:
                for loop in face.loops:
                    uv = loop[uv_layer_index]
                    if uv.select:
                        return True
            return False

        if check_candidate_object():
            to_select.append(obj)

        mesh.free()

    view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one
    set_selection(view_layer.objects, *to_select, synchronize_active=True, make_sure_active=True)


def synchronize_visibility_to_render(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene()
    view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one

    for item in view_layer.objects:
        item.hide_viewport = item.hide_render


def make_everything_visible(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene()
    view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one

    for item in view_layer.objects:
        item.hide_viewport = False


def recalculate_normals(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene()
    view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one

    for workmesh in context.selected_objects:
        clean_normals(context, workmesh)


def update_bake_scene(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene()

    #DECISION - should we clear the bake scene each update?
    #Clear bake scene from meshes (this will remove the objects that own the meshes as ell)
    for obj in bake_scene.collection.objects:
        bpy.data.meshes.remove(obj.data, do_unlink=True)

    #todo note 1
    for bake_target in ht.bake_target_collection:
        _, mt = bake_target.get_mirror_type(ht)
        if mt is MIRROR_TYPE.SECONDARY:
            continue

        source_obj = bake_target.require_object()

        for variant in bake_target.iter_bake_scene_variant_names():

            if variant in bake_scene.objects:
                #Object is already in bake scene - since we clear the bake scene this means two bake targets resolved to the same name
                #TODO - we should validate the state before even starting this operation
                raise Exception("FAIL") #TODO - proper exception

            elif variant in bpy.data.objects:
                #Object is not in bake scene but it does exist, this is a serious issue
                raise Exception(f"Object {variant} already existing") #TODO - proper exception
                #NOTE - this can happen if there is orphaned objects, like if the scene is deleted but not the objects
                #TBD - how should we deal with this situation? Delete conflicting objects? warn user? Instruct user how to resolve situation?

            else:
                #Object is not in bake scene, let's put it there
                new_object = copy_object(source_obj, variant)
                bake_scene.collection.objects.link(new_object)

            #Remove shape keys if we only want a specific one
            if bake_target.shape_key_name:
                for skey in new_object.data.shape_keys.key_blocks:
                    if skey.name != bake_target.shape_key_name:
                        new_object.shape_key_remove(skey)


def synchronize_mirrors(operator: Operator, context: Context, ht: HomeomorphicProperties):
    for mirror in ht.bake_target_mirror_collection:
        primary = ht.bake_target_collection[mirror.primary]
        secondary = ht.bake_target_collection[mirror.secondary]
        if primary and secondary:
            secondary.uv_area_weight = primary.uv_area_weight
            secondary.uv_mode = primary.uv_mode
            secondary.atlas = primary.atlas
            secondary.uv_map = primary.uv_map
            secondary.multi_variants = primary.multi_variants
            copy_collection(primary.variant_collection, secondary.variant_collection, transfer_variant)
            secondary.selected_variant = primary.selected_variant


def reset_uv_transforms(operator: Operator, context: Context, ht: HomeomorphicProperties):
    bake_scene = require_bake_scene()
    view_layer = bake_scene.view_layers[0]	#TODO - make sure there is only one

    to_reset = list()
    for bake_target in ht.bake_target_collection:
        for variant_name, variant in bake_target.iter_variants():
            if variant.workmesh.select_get(view_layer=view_layer):
                to_reset.append(bake_target)

    reset_uv_transformations(to_reset)


def reset_uv_transformations(bake_targets: list[BakeTarget]):
    for bake_target in bake_targets:
        for _, variant in bake_target.iter_variants():
            copy_and_transform_uv(bake_target.source_object, bake_target.source_uv_map, variant.workmesh, variant.uv_map)


def copy_and_transform_uv(
    source_object: Object, source_layer: str,
    target_object: Object, target_layer: str, scale_factor: float = 1.0):

    #TODO - investigate if we can get uv layer index without actually changing it and getting mesh.loops.layers.uv.active
    bpy.ops.object.mode_set(mode="OBJECT")

    #TODO - would be great if we made a context manager for these commands so that we could reset all changes when exiting the context (this applies to a lot of things outside this function too)
    set_uv_map(source_object, source_layer)
    set_uv_map(target_object, target_layer)

    source_mesh = bmesh.new()
    source_mesh.from_mesh(source_object.data)
    source_uv_layer_index = source_mesh.loops.layers.uv.active

    target_mesh = bmesh.new()
    target_mesh.from_mesh(target_object.data)
    target_uv_layer_index = target_mesh.loops.layers.uv.active

    #TODO - use a strict zip here so we can detect error and also handle any such errors using the .free() methods in the finalization handler
    for source_face, target_face in zip(source_mesh.faces, target_mesh.faces):
        for source_loop, target_loop in zip(source_face.loops, target_face.loops):
            source_uv = source_loop[source_uv_layer_index].uv
            target_loop[target_uv_layer_index].uv = source_uv * scale_factor

    target_mesh.to_mesh(target_object.data)
    source_mesh.free()
    target_mesh.free()


def clean_normals(context: Context, object_: Object):
    context.view_layer.objects.active = object_
    bpy.ops.object.mode_set(mode="EDIT", toggle=False)
    bpy.ops.mesh.select_all(action="SELECT")
    # average normals
    bpy.ops.mesh.average_normals(average_type="FACE_AREA")
    # make normals consistent
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)


def copy_uv_layers(operator: Operator, context: Context, ht: HomeomorphicProperties):
    last_edit_mode = bpy.context.mode
    if last_edit_mode == "EDIT_MESH":
        # -- switch to object mode
        bpy.ops.object.mode_set(mode="OBJECT")

    # transfer all missing uv layers from one object to another
    obj, ob = ht.source_object_uv, ht.target_object_uv
    if not obj or not ob:
        return
    last_active = bpy.context.active_object
    last_selection = [(o, o.select_get()) for o in bpy.data.objects]
    # -- select the pertinent objects
    [o.select_set(False) for o in bpy.data.objects]
    ob.select_set(True)
    obj.select_set(True)
    # -- make the source active
    bpy.context.view_layer.objects.active = obj

    # -- transfer uv layers in source not in target
    uv_layer_names = [uv.name for uv in obj.data.uv_layers]
    if uv_layer_names:
        if ob.type =="MESH":
            for uv_map in uv_layer_names:
                obj.data.uv_layers[uv_map].active = True
                if uv_map not in ob.data.uv_layers:
                    ob.data.uv_layers.new(name=uv_map)
                    ob.data.uv_layers[uv_map].active = True
                    bpy.ops.object.join_uvs()

    ob.select_set(False)
    obj.select_set(False)

    # -- restore previous selection and active state
    if last_edit_mode == "EDIT_MESH":
        bpy.ops.object.mode_set(mode="EDIT")

    if last_active:
        bpy.context.view_layer.objects.active = last_active
    if last_selection:
        for o, state in last_selection:
            o.select_set(state)


class FABA_OT_synchronize_uv_to_vertices(FabaOperator):
    bl_label =            "Select mesh vertices based on UV selection"
    bl_idname =           "faba.synchronize_uv_to_vertices"
    bl_description =      "Sync selection state for mesh and uvs"
    faba_operator =       synchronize_uv_to_vertices


class FABA_OT_select_objects_by_uv(FabaOperator):
    bl_label =            "Select objects based on UV selection"
    bl_idname =           "faba.select_objects_by_uv"
    bl_description =      "Select all objects in the active uv"
    faba_operator =       select_objects_by_uv


class FABA_OT_synchronize_visibility_to_render(FabaOperator):
    bl_label =            "Show to render only"
    bl_idname =           "faba.synchronize_visibility_to_render"
    bl_description =      "Will only make objects that are going to be rendered visible in the viewlayer"
    faba_operator =       synchronize_visibility_to_render


class FABA_OT_make_everything_visible(FabaOperator):
    bl_label =            "Show everything"
    bl_idname =           "faba.make_everything_visible"
    bl_description =      "Will make everything in the baking viewlayer visible"
    faba_operator =       make_everything_visible


class FABA_OT_reset_uv_transforms(FabaOperator):
    bl_label =            "Reset UV transforms"
    bl_idname =           "faba.reset_uv_transforms"
    bl_description =      "Resets UV transform to reflect the source object"
    faba_operator =       reset_uv_transforms


class FABA_OT_recalculate_normals(FabaOperator):
    bl_label =            "Recalculate normals on selected meshes"
    bl_idname =           "faba.recalculate_normals"
    bl_description =      "Recalculates normals to combat artifacts"
    faba_operator =       recalculate_normals


class FABA_OT_update_baking_scene(FabaOperator):
    bl_label =            "Update baking scene"
    bl_idname =           "faba.update_baking_scene"
    bl_description =      "Regenerate bake scene objects from bake targets"
    faba_operator =       update_bake_scene


class FABA_OT_synchronize_mirrors(FabaOperator):
    bl_label =            "Synchronize mirrors"
    bl_description =      "Copy settings from all primary targets to secondary targets in the mirror list"
    bl_idname =           "faba.synchronize_mirrors"
    faba_operator =       synchronize_mirrors


class FABA_OT_copy_uv_layers(FabaOperator):
    bl_label =            "Copy UV Layers"
    bl_description =      "Transfer UV layers from one object to another"
    bl_idname =           "faba.copy_uv_layers"
    faba_operator =       copy_uv_layers
