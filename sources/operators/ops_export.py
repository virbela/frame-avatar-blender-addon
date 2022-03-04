import os
import bpy
import json
from ..logging import log_writer as log
from ..helpers import require_bake_scene
from ..mesh_utilities import uv_transformation_calculator, get_uv_map_from_mesh

def export(operator, context, ht):
    obj = ht.source_object
    obj.hide_set(False)
    obj.hide_viewport = False 
    obj.select_set(True)

    uv_transform_extra_data = list()		
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

        uv_transform_extra_data.append((shape.name, dict(UVTransform = uv_transform_map.get(shape_name))))

    morphsets_dict = {f"MorphSets_Avatar": uv_transform_extra_data}
    export_json = json.dumps(morphsets_dict, sort_keys=False, indent=2)
    log.info(export_json)

    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    outputfile = os.path.join(directory , f"Avatar.gltf")
    outputfile_glb = os.path.join(directory , f"Avatar.glb")

    bpy.ops.export_scene.gltf(
        filepath=outputfile, 
        export_format='GLTF_EMBEDDED', 
        export_texcoords=True, 
        export_normals=True, 
        use_selection=True, 
        export_extras=False, 
        export_morph=True, 
        will_save_settings=True
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
        export_texcoords=True, 
        export_normals=True, 
        use_selection=True, 
        export_extras=True, 
        export_morph=True, 
        will_save_settings=True
    )

    bpy.ops.object.delete()
