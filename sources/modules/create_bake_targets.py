import modules.state as state
from modules.utils.string_utils import get_by_name_substring , get_by_name_with_without_substring , int_after_substring
try:
    import bpy
except ImportError:
    import modules.mocks.bpy_mock as bpy

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
    return bpy.data.objects

def create_variant(object):
    pass

def get_variants(layer : list) -> list:
    print("Get Variants")
    variants = []
    # Add variants to the layer
    for i in range(0, len(layer)):
        if "__Variants_" in layer[i].name:
            n = int_after_substring(layer[i].name, "__Variants_")
            print("Variants: " + str(n))
        continue
    return variants
    print("End Get Variants")

def create_bake_targets()-> None:
    print("Create Bake Targets")
    # morphs are meshes based on input object with shape keys
    morphs = get_morph_objects()
    # A list of meshes that are not shaded
    unshaded_group = get_unshaded(morphs)
    # A list of meshes that are shaded but with no color
    grayscale_group = get_grayscale(morphs)
    # A list of meshes that are shaded and with color
    state.set_rgb_layer(get_rgb(morphs))
    state.extend_rgb_layer(get_variants(state.get_rgb_layer()))
    print("End Create Bake Targets")