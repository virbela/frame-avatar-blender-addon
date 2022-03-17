import os
import bpy
import json
from ..logging import log_writer as log
from ..helpers import require_bake_scene, require_work_scene
from ..mesh_utilities import uv_transformation_calculator, get_uv_map_from_mesh


def export(operator, context, ht):
    export_glb(context)
    composite_atlas(context)

def export_glb(context):
    obj = context.active_object
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


    shape_keys = obj.data.shape_keys.key_blocks[1:]
    for shape in shape_keys:
        shape_name = str(shape.name)

        #Strip __None if present
        if shape_name.endswith('__None'):
            shape_name = shape_name[:-6]

        #TODO(ranjian0) Implement variants
        trans = uv_transform_map.get(shape_name)
        uv_transform = dict(UVTransform = None)
        if trans:
            tx, ty, rot, scale = trans
            uv_transform = {
                "UVTransform" : {
                    "scale": scale,
                    "rotation": rot,
                    "translation" : [tx, ty]
                }
            }

        uv_transform_extra_data[shape.name] = uv_transform

    morphsets_dict = {
        "MorphSets_Avatar": {
            "Morphs": uv_transform_extra_data,
            "Filters": dict()
        }
    }

    export_json = json.dumps(morphsets_dict, sort_keys=False, indent=2)
    log.info(export_json)

    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    outputfile = os.path.join(directory , f"morphic_avatar.gltf")
    outputfile_glb = os.path.join(directory , f"morphic_avatar.glb")

    bpy.ops.export_scene.gltf(
        filepath=outputfile, 
        export_format='GLTF_EMBEDDED',
        # disable all default options
        export_texcoords = False,
        export_normals = False,
        export_colors = False,
        export_animations=False,
        export_skins=False,
        export_materials='NONE',
        # enable only what we want
        use_selection=True,
        export_morph=True,
        export_morph_normal=False 
    )
    with open(outputfile, 'r') as openfile:
        json_data = json.load(openfile)

    json_data["extras"] = morphsets_dict

    # save modified GLTF
    with open(outputfile, 'w') as exportfile:
        json.dump(json_data, exportfile, indent=4)

    # open modified GLTF, re-export as GLB
    obj.select_set(False)

    bpy.ops.import_scene.gltf(filepath=outputfile)
    imported_gltf = bpy.context.active_object
    imported_gltf.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=outputfile_glb, 
        export_format='GLB', 
        # disable all default options
        export_texcoords = False,
        export_normals = False,
        export_colors = False,
        export_animations=False,
        export_skins=False,
        export_materials='NONE',
        # valid options
        use_selection=True, 
        export_extras=True, 
        export_morph=True, 
        export_morph_normal=False
    )

    bpy.ops.object.delete()


def composite_atlas(context):
    work_scene = require_work_scene(context)
    # switch on nodes and get reference

    work_scene.use_nodes = True
    tree = work_scene.node_tree

    # clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

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

    # create combine rgba node
    comb_node = tree.nodes.new('CompositorNodeCombRGBA')   
    comb_node.location = 500,0

    # Create file output node
    file_node = tree.nodes.new('CompositorNodeOutputFile')   
    file_node.location = 700,0
    file_node.format.file_format = 'JPEG'
    file_node.format.quality = 100
    file_node.base_path = os.path.dirname(bpy.data.filepath)
    file_node.file_slots[0].path = "useAtlas"

    # link nodes
    links = tree.links
    links.new(image_node_r.outputs[0], comb_node.inputs[0])
    links.new(image_node_g.outputs[0], comb_node.inputs[1])
    links.new(image_node_b.outputs[0], comb_node.inputs[2])
    links.new(comb_node.outputs[0], file_node.inputs[0])

    bpy.ops.render.render(use_viewport=True)

    dirname = os.path.dirname(bpy.data.filepath)
    for f in os.listdir(dirname):
        if 'useAtlas' in f:
            os.rename(
                os.path.join(dirname, f),
                os.path.join(dirname, 'useAtlas.jpg')
            )
