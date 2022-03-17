import os
import bpy
import json
from ..logging import log_writer as log
from ..helpers import require_bake_scene
from ..mesh_utilities import uv_transformation_calculator, get_uv_map_from_mesh

def export(operator, context, ht):
    obj = context.active_object
    obj.hide_set(False)
    obj.hide_viewport = False 
    obj.select_set(True)

    uv_transform_extra_data = dict()		
    uv_transform_map = dict()				

    uvtc = uv_transformation_calculator(get_uv_map_from_mesh(obj))

    bake_scene = require_bake_scene(context)
    for name, item in bake_scene.objects.items():
        print(f'Getting transform for: {name}')
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
    outputfile = os.path.join(directory , f"Avatar.gltf")
    outputfile_glb = os.path.join(directory , f"Avatar.glb")

    bpy.ops.export_scene.gltf(
        filepath=outputfile, 
        export_format='GLTF_EMBEDDED', 
        use_selection=True, 
        export_extras=False, 
        export_morph=True, 
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
        use_selection=True, 
        export_extras=True, 
        export_morph=True, 
    )

    bpy.ops.object.delete()
