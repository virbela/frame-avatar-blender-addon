import os
import bpy
import json
import uuid
from contextlib import contextmanager
from .common import popup_message
from ..logging import log_writer as log
from ..uvtransform import UVTransform, uv_transformation_calculator, get_uv_map_from_mesh
from ..helpers import require_bake_scene, require_work_scene, is_dev, get_bake_target_variant_name


def export(operator, context, ht):
    try:
        if export_glb(context, ht):
            composite_atlas(context)
    except FileExistsError:
        popup_message("Export files already exist in the current folder!") 
    except PermissionError:
        popup_message("Please save the current blend file!")

def export_glb(context, ht):
    obj = context.active_object

    if not obj.data.shape_keys:
        #XXX Probably Not the main avatar object
        popup_message("Selected object is not an Homeomorphic avatar", 'Context Error')
        return False
    
    if obj.name != 'Avatar':
        #XXX Probably Not the main avatar object
        popup_message("Avatar object name invalid! Try 'Avatar'.", 'Context Error')
        return False

    obj.hide_set(False)
    obj.hide_viewport = False 
    obj.select_set(True)

    uv_transform_extra_data = dict()		
    uv_transform_map = dict()				

    uvtc = uv_transformation_calculator(get_uv_map_from_mesh(obj))

    bake_scene = require_bake_scene(context)
    for name, item in bake_scene.objects.items():
        log.info(f'Getting transform for: {name}')
        uv_transform_map[name] = uvtc.calculate_transform(get_uv_map_from_mesh(item))

    def get_transform(shape_name):
        if shape_name.endswith('__None'):
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

    def get_variant_channel(variant):
        if variant.uv_target_channel == 'UV_TARGET_COLOR':
            return (0, 0, 0, 1)
        elif variant.uv_target_channel == 'UV_TARGET_R':
            return (1, 0, 0, 0)
        elif variant.uv_target_channel == 'UV_TARGET_G':
            return (0, 1, 0, 0)
        elif variant.uv_target_channel == 'UV_TARGET_B':
            return (0, 0, 1, 0)
        else:
            return (0, 0, 0, 0)

    for bake_target in ht.bake_target_collection:
        result = None
        if bake_target.multi_variants:            
            variants = {'Variants': {}}
            for variant in bake_target.variant_collection:
                shape_name = get_bake_target_variant_name(bake_target, variant)
                variants['Variants'][variant.name] = get_transform(shape_name)
                variants['Variants'][variant.name]['UVChannel'] = get_variant_channel(variant)
            result = variants
        else:
            variant = bake_target.variant_collection[0]
            shape_name = get_bake_target_variant_name(bake_target, variant)
            result = get_transform(shape_name)
            result['UVChannel'] = get_variant_channel(variant)
                
        uv_transform_extra_data[bake_target.shortname] = result

    for bake_target in ht.bake_target_collection:
        if bake_target.bake_mode == 'UV_BM_MIRRORED':
            # -- set the uv transform to opposite mirror
            base = bake_target.name[:-2]
            Rk = f'{base}_L' if '_R' in bake_target.name else f'base_R'
            R = ht.bake_target_collection.get(Rk)
            if not R:
                log.info(f'Missing mirror source for {bake_target}')
                continue
            uv_transform_extra_data[bake_target.shortname] = uv_transform_extra_data[R.shortname]
            uv_transform_extra_data[bake_target.shortname]['is_mirror'] = True

    # build effects
    for effect in ht.effect_collection:
        effect_verts = calculate_effect_delta(obj, effect)
        data = {
            effect.name: {
                "ids": [v[0] for v in effect_verts],
                "positions": [v[1] for v in effect_verts]
            }
        }
        uv_transform_extra_data[effect.parent_shapekey]['effects'] = data

    morphsets_dict = {
        "Morphs": uv_transform_extra_data,
        "Filters": dict()
    }

    export_json = json.dumps(morphsets_dict, sort_keys=False, indent=2)
    log.info(export_json)

    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)

    outputfile_glb = os.path.join(directory , "morphic_avatar.glb")

    with clear_custom_props(obj):
        obj['MorphSets_Avatar'] = morphsets_dict

        bpy.ops.export_scene.gltf(
            filepath=outputfile_glb, 
            export_format='GLB', 
            # disable all default options
            export_texcoords = True,
            export_normals = False,
            export_colors = False,
            export_animations=False,
            export_skins=False,
            export_materials='NONE',
            # valid options
            use_selection=True, 
            export_extras=True, 
            export_morph=True,
        )

        if is_dev():
            # Check gltf export
            bpy.ops.export_scene.gltf(
                filepath=os.path.join(directory , "morphic_avatar.gltf"), 
                export_format='GLTF_EMBEDDED', 
                # disable all default options
                export_texcoords = True,
                export_normals = False,
                export_colors = False,
                export_animations=False,
                export_skins=False,
                export_materials='NONE',
                # valid options
                use_selection=True, 
                export_extras=True, 
                export_morph=True,
            )

    return True


def composite_atlas(context):
    work_scene = require_work_scene(context)

    work_scene.use_nodes = True
    tree = work_scene.node_tree

    # clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    atlases = (
        'atlas_intermediate_red', 
        'atlas_intermediate_green', 
        'atlas_intermediate_blue', 
        'atlas_intermediate_color'
    )
    missing = []
    for img in atlases:
        if img not in bpy.data.images:
            missing.append(img)

    if missing:
        missing_atlas_names = ', '.join([at.split('_')[-1] for at in missing])
        popup_message(f"Atlases [ {missing_atlas_names} ] not found!", title="Export Error")
        return

    # create input image node
    # TODO(ranjian0) Ensure images exists, warn otherwise
    image_node_r = tree.nodes.new(type='CompositorNodeImage')
    image_node_r.image = bpy.data.images['atlas_intermediate_red']
    image_node_r.location = 0,0

    image_node_g = tree.nodes.new(type='CompositorNodeImage')
    image_node_g.image = bpy.data.images['atlas_intermediate_green']
    image_node_g.location = 150,-150

    image_node_b = tree.nodes.new(type='CompositorNodeImage')
    image_node_b.image = bpy.data.images['atlas_intermediate_blue']
    image_node_b.location = 300,-300

    image_node_color = tree.nodes.new(type='CompositorNodeImage')
    image_node_color.image = bpy.data.images['atlas_intermediate_color']
    image_node_color.location = 450,-450

    # create combine rgba node
    comb_node = tree.nodes.new('CompositorNodeCombRGBA')   
    comb_node.location = 500,0

    mult_node = tree.nodes.new('CompositorNodeMixRGB')
    mult_node.blend_type = 'MULTIPLY'
    mult_node.location = 700, 0

    # Create file output node
    file_node = tree.nodes.new('CompositorNodeOutputFile')   
    file_node.location = 900,0
    file_node.format.file_format = 'JPEG'
    file_node.format.quality = 100
    file_node.base_path = os.path.dirname(bpy.data.filepath)
    file_node.file_slots[0].path = "hasAtlas"

    # link nodes
    links = tree.links
    links.new(image_node_r.outputs[0], comb_node.inputs[0])
    links.new(image_node_g.outputs[0], comb_node.inputs[1])
    links.new(image_node_b.outputs[0], comb_node.inputs[2])
    links.new(comb_node.outputs[0], mult_node.inputs[1])
    links.new(image_node_color.outputs[0], mult_node.inputs[2])
    links.new(mult_node.outputs[0], file_node.inputs[0])

    bpy.ops.render.render(use_viewport=True)

    dirname = os.path.dirname(bpy.data.filepath)
    for f in os.listdir(dirname):
        if 'hasAtlas' in f:
            os.rename(
                os.path.join(dirname, f),
                os.path.join(dirname, 'hasAtlas.jpg')
            )

@contextmanager
def clear_custom_props(item):
    prop_keys = list(item.keys())

    # remove all custom props
    props = dict()
    for key in prop_keys:
        props[key] = item.pop(key)

    yield

    # reset props
    for k,v in props.items():
        item[k] = v


def calculate_effect_delta(obj, effect):
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
        if diff > 1e-3:
            result.append((ep[0], ep[1].to_tuple()))

    bpy.data.meshes.remove(base_obj.data, do_unlink=True)
    bpy.data.meshes.remove(effect_obj.data, do_unlink=True)
    return result

def obj_from_shapekey(obj, keyname):
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

    bpy.context.scene.collection.objects.link(pending_object)
    return pending_object
