from modules.utils.string_utils import get_by_name_substring , get_by_name_with_without_substring , int_after_substring
try:
    import bpy
except ImportError:
    bpy = None

import modules.mocks.object_mock as object_mock
mesh = object_mock.Mesh()

def get_morph_objects() -> list:
    # Using bpy.data.objects[]
    return []

def get_unshaded(morphs : list) -> list:
    # use GetByNameSubstring("__None", morphs)
    return morphs

def get_grayscale(morphs : list) -> list:
    # use GetByNameWithWithoutSubstring([], ["__None","__TakesColor"], morphs)
    return morphs

def get_rgb(morphs : list) -> list:
    # use GetByNameSubstring("__TakesColor", morphs)
    return [mesh]

def create_variant(object):
    pass

def add_variants(layer : list) -> None:
    print("Add Variants")
    # Add variants to the layer
    for i in range(0, len(layer)):
        if "__Variants_" in layer[i].name:
            n = int_after_substring(layer[i].name, "__Variants_")
            print("Variants: " + str(n))
        continue
    print("End Add Variants")

def create_bake_targets()-> None:
    print("Create Bake Targets")
    # morphs are meshes based on input object with shape keys
    morphs = get_morph_objects()
    # A list of meshes that are not shaded
    unshaded_group = get_unshaded(morphs)
    # A list of meshes that are shaded but with no color
    grayscale_group = get_grayscale(morphs)
    # A list of meshes that are shaded and with color
    rgb_group = get_rgb(morphs)
    rgb_layer = rgb_group
    add_variants(rgb_layer)
    print("End Create Bake Targets")