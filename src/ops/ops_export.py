import os
import bpy
import json
import uuid
import tempfile
from pathlib import Path
from collections import defaultdict
from contextlib import contextmanager
from bpy.types import Operator, Context, Object, Scene

from .base import FabaOperator
from ..utils.logging import log
from ..utils.bone_animation import BoneAnimationExporter
from ..utils.bake_targets import validate_bake_target_setup
from ..utils.contextutils import active_object, selection, active_scene
from ..utils.helpers import ensure_applied_rotation, get_prefs, popup_message
from ..utils.morph_spec import validate_floater_morphs, validate_fullbody_morphs
from ..utils.uvtransform import UVTransform, UVTransformationCalculator, get_uv_map_from_mesh
from ..props import BakeTarget, HomeomorphicProperties, BakeVariant, PositionEffect, ColorEffect
from ..utils.helpers import require_bake_scene, require_work_scene, is_dev, get_bake_target_variant_name, get_animation_objects


def export(operator: Operator, context: Context, HT: HomeomorphicProperties):
    HT.export_progress_start()
    context.window.cursor_set("WAIT")
    view_layer = require_work_scene().view_layers[0]

    def on_exit():
        HT.export_progress_end()
        context.window.cursor_set("DEFAULT")

    if not validate_export(context, HT):
        return

    deselect_all()
    with selection(None, view_layer), active_object(None, view_layer):
        try:
            if HT.should_export_animation_action():
                BoneAnimationExporter(context, HT)

            if HT.should_export_animation_json():
                BoneAnimationExporter.load_from_json(context, HT)

            if HT.export_glb:
                with active_scene(require_work_scene().name):
                    success = export_glb(context, HT)
                    if not success:
                        # XXX exit early if mesh export failed
                        on_exit()
                        return

            if HT.export_atlas:
                export_atlas(context, denoise=HT.denoise)
            
            on_exit()
        except FileExistsError:
            popup_message("Export files already exist in the current folder!")
            on_exit()
        except PermissionError:
            popup_message("Please save the current blend file!")
            on_exit()
        except Exception as e:
            on_exit()
            raise e


def validate_export(context: Context, HT: HomeomorphicProperties) -> bool:
    log.info("Validating Export state...")
    work_scene = require_work_scene()
    if work_scene is None:
        popup_message("Export validation failed! Work scene missing!", "Validation Error")
        return False

    # XXX Allow export from the bake scene
    # active_scene = context.scene
    # if active_scene != work_scene:
    #     popup_message("Export validation failed! Must be in main scene!", "Validation Error")
    #     return False

    if HT.avatar_mesh is None:
        popup_message("Export validation failed! Avatar Object not selected in workflow panel!", "Validation Error")
        return False

    if HT.avatar_type == "FULLBODY" and HT.avatar_rig is None:
        popup_message("Export validation failed! Avatar Rig not selected in workflow panel!", "Validation Error")
        return False

    prefs = get_prefs()
    if prefs.custom_frame_validation:
        # check that the avatar shapekeys match the expected morph_spec
        if HT.avatar_type == "FULLBODY":
            if not validate_fullbody_morphs(HT.avatar_mesh):
                return False
        elif HT.avatar_type == "FLOATER":
            if not validate_floater_morphs(HT.avatar_mesh):
                return False

        if not validate_bake_target_setup(HT):
            return False
        
    # -- check for invalid transform for the avatar_mesh

    # -- check for missing mouth animation

    # -- check for duplicate actions when we are exporting from actions
    if HT.should_export_animation_action():
        # --ensure actions are valid with no duplicates
        pass

    # -- check conforming weights if we are exporting from JSON files
    if HT.should_export_animation_json():
        pass
        
    return True


def export_glb(context: Context, ht: HomeomorphicProperties) -> bool:
    obj = ht.avatar_mesh
    view_layer = require_work_scene().view_layers[0]
    ensure_applied_rotation(obj)

    if not obj.data.shape_keys:
        #XXX Probably Not the main avatar object
        popup_message("Selected object is not an Homeomorphic avatar", "Context Error")
        return False

    obj.hide_set(False)
    obj.hide_viewport = False
    obj.select_set(True, view_layer=view_layer)

    uv_transform_metadata = get_uvtransform_metadata(context, ht, obj)
    effects_metadata = get_effects_metadata(ht, obj)

    # -- merge the metadata
    for morph_name, effect_data in effects_metadata.items():
        ht.export_progress_step(0.1)
        if morph_name in uv_transform_metadata.keys():
            data = uv_transform_metadata[morph_name]
            if "effects" not in data.keys():
                data["effects"] = dict()

            for effect_name, effect_props in effect_data.items():
                data["effects"][effect_name] = effect_props

    morphsets_dict = {
        "Morphs": uv_transform_metadata,
    }


    if ht.avatar_type == "FULLBODY" and ht.export_animation:
        morphsets_dict["Animation"] = animation_metadata(ht)

        if ht.export_animation_preview:
            # XXX Rename exported animation to idle (if many, pick the first one)
            keys = list(morphsets_dict["Animation"]["bone_transforms"].keys())
            if len(keys):
                anim = keys[0]
                transforms = morphsets_dict["Animation"]["bone_transforms"].pop(anim)
                morphsets_dict["Animation"]["bone_transforms"]["idle"] = transforms


    prefs = get_prefs()
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    if os.path.exists(prefs.glb_export_dir):
        directory = str(Path(prefs.glb_export_dir).absolute())

    fname = "faba_avatar.glb"
    if ht.avatar_type == "FLOATER":
        fname = "faba_floater_avatar.glb"
    outputfile_glb = os.path.join(directory , fname)

    obj = ht.avatar_mesh
    with selection([obj], view_layer=view_layer), active_object(obj, view_layer=view_layer):
        with clear_custom_props(obj):
            obj["MorphSets_Avatar"] = morphsets_dict
            log.info(f"Exporting avatar to {outputfile_glb}")
            bpy.ops.export_scene.gltf(
                filepath=outputfile_glb,
                export_format="GLB",
                # disable all default options
                export_texcoords = True,
                export_normals = False,
                export_colors = False,
                export_animations=False,
                export_skins=False,
                export_materials="NONE",
                # valid options
                use_selection=True,
                export_extras=True,
                export_morph=True,
                use_active_scene=True
            )
            ht.export_progress_step(5)

            if is_dev():
                directory = os.path.dirname(filepath)
                export_json = json.dumps(morphsets_dict, sort_keys=False, indent=2)
                with open(os.path.join(directory, "morphs.json"), "w") as f:
                    print(export_json, file=f)

                # Check gltf export
                bpy.ops.export_scene.gltf(
                    filepath=os.path.join(directory , "morphic_avatar.gltf"),
                    export_format="GLTF_EMBEDDED",
                    # disable all default options
                    export_texcoords = True,
                    export_normals = False,
                    export_colors = False,
                    export_animations=False,
                    export_skins=False,
                    export_materials="NONE",
                    # valid options
                    use_selection=True,
                    export_extras=True,
                    export_morph=True,
                    use_active_scene=True
                )

    # TODO(ranjian0) 
    # DEPRECATED should remove
    # -- cleanup animation shapekeys
    last_idx = obj.active_shape_key_index
    for kb in obj.data.shape_keys.key_blocks:
        if kb.name.startswith("fabanim."):
            log.info(f"Post Export Removing .. {kb.name}")
            obj.shape_key_remove(kb)
    obj.active_shape_key_index = last_idx

    return True


def export_atlas(context: Context, denoise: bool = True):
    work_scene = require_work_scene()

    work_scene.use_nodes = True
    tree = work_scene.node_tree

    # clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    atlases = (
        "atlas_intermediate_red",
        "atlas_intermediate_green",
        "atlas_intermediate_blue",
        "atlas_intermediate_color"
    )
    missing = []
    for img in atlases:
        if img not in bpy.data.images:
            missing.append(img)

    if missing:
        missing_atlas_names = ", ".join([at.split("_")[-1] for at in missing])
        popup_message(f"Atlases [ {missing_atlas_names} ] not found!", title="Export Error")
        return

    # create input image node
    # TODO(ranjian0) Ensure images exists, warn otherwise
    image_node_r = tree.nodes.new(type="CompositorNodeImage")
    image_node_r.image = bpy.data.images["atlas_intermediate_red"]
    image_node_r.location = 0,0

    image_node_r_denoise = tree.nodes.new(type="CompositorNodeDenoise")
    image_node_r_denoise.location = 200, 150
    image_node_r_denoise.use_hdr = False
    image_node_r_denoise.prefilter = "NONE"

    image_node_g = tree.nodes.new(type="CompositorNodeImage")
    image_node_g.image = bpy.data.images["atlas_intermediate_green"]
    image_node_g.location = 150,-150

    image_node_g_denoise = tree.nodes.new(type="CompositorNodeDenoise")
    image_node_g_denoise.location = 350, 0
    image_node_g_denoise.use_hdr = False
    image_node_g_denoise.prefilter = "NONE"

    image_node_b = tree.nodes.new(type="CompositorNodeImage")
    image_node_b.image = bpy.data.images["atlas_intermediate_blue"]
    image_node_b.location = 300,-300

    image_node_b_denoise = tree.nodes.new(type="CompositorNodeDenoise")
    image_node_b_denoise.location = 500, -150
    image_node_b_denoise.use_hdr = False
    image_node_b_denoise.prefilter = "NONE"

    image_node_color = tree.nodes.new(type="CompositorNodeImage")
    image_node_color.image = bpy.data.images["atlas_intermediate_color"]
    image_node_color.location = 450,-450

    image_node_color_denoise = tree.nodes.new(type="CompositorNodeDenoise")
    image_node_color_denoise.location = 650, -300
    image_node_color_denoise.use_hdr = False
    image_node_color_denoise.prefilter = "NONE"

    # create combine rgba node
    comb_node = tree.nodes.new("CompositorNodeCombRGBA")
    comb_node.location = 700,0

    mult_node = tree.nodes.new("CompositorNodeMixRGB")
    mult_node.blend_type = "MULTIPLY"
    mult_node.location = 900, 0

    # Create file output node
    prefs = get_prefs()
    directory = os.path.dirname(bpy.data.filepath)
    if os.path.exists(prefs.atlas_export_dir):
        directory = str(Path(prefs.atlas_export_dir).absolute())

    file_node = tree.nodes.new("CompositorNodeOutputFile")
    file_node.location = 1100,0
    file_node.format.file_format = "PNG"
    file_node.format.color_mode = "RGB"
    file_node.format.quality = 100
    file_node.base_path = directory
    file_node.file_slots[0].path = "hasAtlas"

    # link nodes
    links = tree.links
    if denoise:
        links.new(image_node_r.outputs[0], image_node_r_denoise.inputs[0])
        links.new(image_node_r_denoise.outputs[0], comb_node.inputs[0])

        links.new(image_node_g.outputs[0], image_node_g_denoise.inputs[0])
        links.new(image_node_g_denoise.outputs[0], comb_node.inputs[1])

        links.new(image_node_b.outputs[0], image_node_b_denoise.inputs[0])
        links.new(image_node_b_denoise.outputs[0], comb_node.inputs[2])

        links.new(comb_node.outputs[0], mult_node.inputs[1])
        links.new(image_node_color.outputs[0], image_node_color_denoise.inputs[0])
        links.new(image_node_color_denoise.outputs[0], mult_node.inputs[2])

        links.new(mult_node.outputs[0], file_node.inputs[0])
    else:
        links.new(image_node_r.outputs[0], comb_node.inputs[0])
        links.new(image_node_g.outputs[0], comb_node.inputs[1])
        links.new(image_node_b.outputs[0], comb_node.inputs[2])
        links.new(comb_node.outputs[0], mult_node.inputs[1])
        links.new(image_node_color.outputs[0], mult_node.inputs[2])
        links.new(mult_node.outputs[0], file_node.inputs[0])

    bpy.ops.render.render(use_viewport=True)

    dirname = os.path.dirname(bpy.data.filepath)
    for f in os.listdir(dirname):
        if "hasAtlas" in f:
            os.rename(
                os.path.join(dirname, f),
                os.path.join(dirname, "hasAtlas.png")
            )


@contextmanager
def clear_custom_props(item: Object | Scene):
    prop_keys = list(item.keys())

    # remove all custom props
    props = dict()
    for key in prop_keys:
        props[key] = item.pop(key)

    yield

    # reset props
    for k,v in props.items():
        item[k] = v


def calculate_effect_delta(obj: Object, effect: PositionEffect) -> list[tuple[int, tuple[float]]]:
    """ Return ids and final positions of all transformed verts of target shapekey relative to base shapekey
    """

    base = obj.data.shape_keys.key_blocks.get(effect.parent_shapekey)
    if not base:
        popup_message(f"Object has no shapkey {effect.parent_shapekey}")

    ef = obj.data.shape_keys.key_blocks.get(effect.effect_shapekey)
    if not ef:
        popup_message(f"Object has no shapkey {effect.effect_shapekey}")

    base_obj = obj_from_shapekey(obj, effect.parent_shapekey)
    effect_obj = obj_from_shapekey(obj, effect.effect_shapekey)

    base_positions = sorted([(v.index, v.co) for v in base_obj.data.vertices], key=lambda v: v[0])
    effect_positions = sorted([(v.index, v.co) for v in effect_obj.data.vertices], key=lambda v: v[0])

    result = []
    for bp, ep in zip(base_positions, effect_positions):
        bpc = bp[1]
        epc = ep[1]

        diff = (bpc - epc).length
        if diff > 0.003:
            result.append((ep[0], ep[1].to_tuple()))

    bpy.data.meshes.remove(base_obj.data, do_unlink=True)
    bpy.data.meshes.remove(effect_obj.data, do_unlink=True)

    # XXX Debug View Selected Verts
    # import bmesh
    # me = base_obj.data
    # bm = bmesh.new()
    # bm.from_mesh(me)
    # for i, v in enumerate(bm.verts):
    #     v.select_set(False)
    #     if v.index in [r[0] for r in result]:
    #         v.select_set(True)

    # bm.select_mode |= {"VERT"}
    # bm.select_flush_mode()
    # bm.to_mesh(me)
    # bm.free()
    return result


def get_verts_or_vgroup(obj: Object, color_effect: ColorEffect) -> list[tuple[int, list]]:
    data = sorted([(v.index, list(color_effect.color)[:3]) for v in obj.data.vertices], key=lambda v: v[0])

    if not color_effect.vert_group:
        # no vert weights, return all verts
        return data

    def filter_by_vgroup(data):
        index, _ = data
        group = obj.vertex_groups.get(color_effect.vert_group)
        try:
            group.weight(index)
        except RuntimeError:
            # current vert not in vgroup
            return False
        return True

    # only the vertices with a weight in the vert group
    data_only_in_group = filter(filter_by_vgroup, data)
    return list(data_only_in_group)


def obj_from_shapekey(obj: Object, keyname: str):
    scene = require_work_scene()
    view_layer = scene.view_layers[0]

    pending_object = obj.copy()
    pending_object.name = f"{keyname}_effect_object_{uuid.uuid4()}"
    pending_object.data = obj.data.copy()
    pending_object.data.name = f"{keyname}_effect_object_{uuid.uuid4()}"

    #Remove all shapekeys except the one this object represents
    for key in pending_object.data.shape_keys.key_blocks:
        if key.name != keyname:
            pending_object.shape_key_remove(key)

    #Remove remaining
    for key in pending_object.data.shape_keys.key_blocks:
        pending_object.shape_key_remove(key)

    scene.collection.objects.link(pending_object)

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "mesh.glb")

        with selection([pending_object], view_layer), active_object(pending_object, view_layer):
            log.info(f"Exporing effect object {pending_object.name}")
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                export_format="GLB",
                # disable all default options
                export_texcoords = True,
                export_normals = False,
                export_colors = False,
                export_animations=False,
                export_skins=False,
                export_materials="NONE",
                # valid options
                use_selection=True,
                export_extras=False,
                export_morph=False,
            )
            bpy.data.meshes.remove(pending_object.data, do_unlink=True)

            log.info("Reimporting effect ...")
            with active_scene(scene.name):
                bpy.ops.import_scene.gltf(filepath=filepath)
                pending_object = bpy.context.object

    return pending_object


def animation_metadata(ht: HomeomorphicProperties) -> dict:
    result = dict()
    animated_objects = get_animation_objects(ht)
    result["layers"] = sorted(o.name for o in animated_objects)
    result["weights"] = BoneAnimationExporter.weights
    result["bone_transforms"] = BoneAnimationExporter.transforms
    result["head_transforms"] = BoneAnimationExporter.head_transforms
    return result


def get_uvtransform_metadata(context: Context, ht: HomeomorphicProperties, obj: Object) -> dict:
    uv_transform_map = dict()
    uv_transform_extra_data = dict()

    uvtc = UVTransformationCalculator(get_uv_map_from_mesh(obj))

    valid_workmeshes = []
    for bake_target in ht.bake_target_collection:
        if bake_target.multi_variants:
            for variant in bake_target.variant_collection:
                valid_workmeshes.append(variant.workmesh)
        else:
            variant = bake_target.variant_collection[0]
            valid_workmeshes.append(variant.workmesh)

    bake_scene = require_bake_scene()
    for name, item in bake_scene.objects.items():
        if item.type != "MESH":
            continue

        if item not in valid_workmeshes:
            continue

        uv_transform_map[name] = uvtc.calculate_transform(get_uv_map_from_mesh(item))

    def get_transform(shape_name: str) -> dict:
        if shape_name.endswith("__None"):
            shape_name = shape_name[:-6]

        trans: UVTransform = uv_transform_map.get(shape_name)
        uv_transform = dict(UVTransform = None)
        if trans:
            uv_transform = {
                "UVTransform" : {
                    "scale": trans.scale,
                    "rotation": trans.rotation,
                    "centroid": list(trans.centroid),
                    "translation" : list(trans.translation)
                }
            }
        return uv_transform

    def get_variant_channel(bk: BakeTarget,variant: BakeVariant) -> tuple[int]:
        if variant.uv_target_channel == "UV_TARGET_COLOR":
            return (0, 0, 0, 1)
        elif variant.uv_target_channel == "UV_TARGET_R":
            return (1, 0, 0, 0)
        elif variant.uv_target_channel == "UV_TARGET_G":
            return (0, 1, 0, 0)
        elif variant.uv_target_channel == "UV_TARGET_B":
            return (0, 0, 1, 0)
        # XXX Get here only for variants with NIL uv islands i.e items with `__None` suffix
        if bk.uv_mode != "UV_IM_NIL":
            log.fatal(f"Invalid UV channel for {bk.name}")
        log.info(f"NIL UV Channel for {bk.name}")
        return (0, 0, 0, 0)

    effect_names = [pos.effect_shapekey for e in ht.effect_collection for pos in e.positions]
    for bake_target in ht.bake_target_collection:
        ht.export_progress_step(0.5)
        if not bake_target.export:
            continue

        if "effect" in bake_target.shortname.lower() or bake_target.shortname.lower() in effect_names:
            log.info("Skipping effect bake target")
            continue

        result = None
        if bake_target.multi_variants:
            variants = {"Variants": {}}
            for variant in bake_target.variant_collection:
                shape_name = get_bake_target_variant_name(bake_target, variant)
                variants["Variants"][variant.name] = get_transform(shape_name)
                variants["Variants"][variant.name]["UVChannel"] = get_variant_channel(bake_target, variant)
            result = variants
        else:
            variant = bake_target.variant_collection[0]
            shape_name = get_bake_target_variant_name(bake_target, variant)
            result = get_transform(shape_name)
            result["UVChannel"] = get_variant_channel(bake_target, variant)

        uv_transform_extra_data[bake_target.shortname] = result

    for bake_target in ht.bake_target_collection:
        if bake_target.bake_mode == "UV_BM_MIRRORED":
            # -- set the uv transform to opposite mirror
            if bake_target.name.lower().endswith("_left"):
                base = bake_target.name[:-5]
                Rk = f"{base}_Right" # assumes title case
            elif bake_target.name.lower().endswith("_right"):
                base = bake_target.name[:-6]
                Rk = f"{base}_Left" # assumes title case
            elif bake_target.name.lower().endswith("_l") or bake_target.name.lower().endswith("_r"):
                base = bake_target.name[:-2]
                Rk = f"{base}_L" if bake_target.name.lower().endswith("_r") else f"{base}_R"
            else:
                log.info(f"Could not find determine mirror target {bake_target.shortname}")
                continue 

            R = ht.bake_target_collection.get(Rk)
            if not R:
                log.info(f"Missing mirror source for {bake_target.shortname}")
                continue
            uv_transform_extra_data[bake_target.shortname] = uv_transform_extra_data[R.shortname]
            uv_transform_extra_data[bake_target.shortname]["is_mirror"] = True

    return uv_transform_extra_data


def get_effects_metadata(ht: HomeomorphicProperties, obj: Object) -> dict:
    log.info("Generating effects ...")
    effects_medatata = defaultdict(dict)
    for effect in ht.effect_collection:
        if effect.type == "POSITION":
            for pos in effect.positions:
                ht.export_progress_step(1.0)
                effect_verts = calculate_effect_delta(obj, pos)
                data = {
                    "type": "POSITION",
                    "ids": [v[0] for v in effect_verts],
                    "data": [v[1] for v in effect_verts]
                }
                effects_medatata[pos.parent_shapekey][effect.name.lower().strip(" ")] = data
        elif effect.type == "COLOR":
            for col in effect.colors:
                ht.export_progress_step(1.0)
                effect_verts = get_verts_or_vgroup(obj, col)
                data = {
                    "type": "COLOR",
                    "ids": [v[0] for v in effect_verts],
                    "data": [v[1] for v in effect_verts]
                }
                effects_medatata[col.shape][effect.name.lower().strip(" ")] = data

    return effects_medatata


def deselect_all():
    for sc in bpy.data.scenes:
        vl = sc.view_layers[0]
        for obj in sc.objects:
            obj.select_set(False, view_layer=vl)


class ExportAnimationJSONPaths:

    def add_json_path(operator: Operator, context: Context, ht: HomeomorphicProperties):
        ht.export_animation_json_paths.add()

    def remove_json_path(operator: Operator, context: Context, ht: HomeomorphicProperties):
        ht.export_animation_json_paths.remove(operator.index)


class FABA_OT_export(FabaOperator):
    bl_label =            "Export GLTF"
    bl_idname =           "faba.export"
    bl_description =      "Export avatar meshes and metadata"
    faba_operator =       export


class FABA_OT_remove_export_json_path(FabaOperator):
    bl_label =            "-"
    bl_description =      "Remove JSON path"
    bl_idname =           "faba.remove_json_path"
    faba_operator =       ExportAnimationJSONPaths.remove_json_path

    index:                bpy.props.IntProperty()


class FABA_OT_add_export_json_path(FabaOperator):
    bl_label =            "+"
    bl_description =      "Add JSON path"
    bl_idname =           "faba.add_json_path"
    faba_operator =       ExportAnimationJSONPaths.add_json_path
