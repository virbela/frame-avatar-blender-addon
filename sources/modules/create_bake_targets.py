import modules.state as state
import modules.data_classes as dc
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

def create_ao_texture(object) -> None:
    print("Create AO Texture")
    # Create a 1k texture for the AO of the object
    ao_tex = bpy.data.images.new(object.name, 1024, 1024) 
    state.add_ao_texture(
        dc.AOTexture(ao_tex.name, object.name)
    ) 
    print("End Create AO Texture")

def create_paint_texture(object, is_color: bool) -> None:
    print("Create Paint Texture")
    # Create a 1k texture for the paint of the object
    paint_tex = bpy.data.images.new(object.name, 1024, 1024) 
    state.add_paint_texture(
        dc.PaintTexture(paint_tex.name, object.name, is_color)
    ) 
    print("End Create Paint Texture")

def create_textures() -> None:
    print("Create Textures")
    # Create textures for the r_layer, g_layer, b_layer
    for object in state.get_r_layer():
        create_ao_texture(object)
        create_paint_texture(object, False)
    for object in state.get_g_layer():
        create_ao_texture(object)
        create_paint_texture(object, False)
    for object in state.get_b_layer():
        create_ao_texture(object)
        create_paint_texture(object, False)
    # Create textures for the rgb_layer
    for object in state.get_rgb_layer():
        create_ao_texture(object)
        create_paint_texture(object, True)
    print("End Create Textures")

def create_ao_material(object) -> None:
    print("Create AO Material")
    # Create AO material and iteratively bake AO to new 1k texture for every shape key mesh.
    #state get texture, bpy.data.textures.data.images['']
    print("End Create AO Material")


def create_bake_targets()-> None:
    print("Create Bake Targets")
    # morphs are meshes based on input object with shape keys
    morphs = get_morph_objects()
    # Pack all textures into blend file: bpy.ops.file.autopack_toggle()
    # Iterate over the shape keys using get_shape_keys() 
	# Filter out the Nones, create layers
	# Filter out the variants, using string helper function after the string create_variant()
	# for every mesh represented in the layers create two 1k textures, one diffuse and one AO, from the shape keys
    # A list of meshes that are not shaded
    unshaded_group = get_unshaded(morphs)
    # A list of meshes that are shaded but with no color
    grayscale_group = get_grayscale(morphs)
    # A list of meshes that are shaded and with color
    state.set_rgb_layer(get_rgb(morphs))
    state.extend_rgb_layer(get_variants(state.get_rgb_layer()))
    partition_grayscale_group(grayscale_group)
    create_textures()
    # Discard AO material and iteratively create a new unique paint material for every shape key mesh, assign the baked AO textures to a materail setup. assign paint texture .  
    create_ao_material()
    print("End Create Bake Targets")