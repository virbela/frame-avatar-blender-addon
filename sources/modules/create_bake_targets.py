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

def create_variant(object,i) :
    variant = None
    # variant = object.copy()
    # variant.name = object.name + "__Variant_" + str(i)
    return variant

def create_n_variants(object, n) -> list:
    variants = []
    for i in range(1, n):
        variants.append(create_variant(object,i))
    return variants

def get_variants(layer : list) -> list:
    print("Get Variants")
    variants = []
    # Add variants to the layer
    for i in range(0, len(layer)):
        if "__Variants_" in layer[i].name:
            n = int_after_substring(layer[i].name, "__Variants_")
            print("Variants: " + str(n))
            variants.extend(create_n_variants(layer[i], n-1))
        continue
    return variants
    print("End Get Variants")

def n_equal_sum_partitions(n :int, lst: list, d: float) -> list:
    partitions = []
    # returns list of lists containing the partitions of the grayscale_group
    return partitions

def partition_grayscale_group(grayscale_group : list) -> None:
    r_layer = []
    g_layer = []
    b_layer = []
    # Partition grayscale_group into r_layer, g_layer, b_layer
    partitions = n_equal_sum_partitions(3, grayscale_group, 1.0)
    r_layer = partitions[0]
    g_layer = partitions[1]
    b_layer = partitions[2]
    state.set_r_layer(r_layer)
    state.set_g_layer(g_layer)
    state.set_b_layer(b_layer)

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