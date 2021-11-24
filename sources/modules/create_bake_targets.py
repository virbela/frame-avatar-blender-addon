from modules.utils.string_utils import GetByNameSubstring , GetByNameWithWithoutSubstring , IntAfterSubstring
try:
    import bpy
except ImportError:
    bpy = None
    import modules.mocks.object_mock as object_mock
    mesh = object_mock.Mesh()

def GetMorphObject():
    # Using bpy.data.objects[]
    return []

def GetUnshaded(morphs):
    # use GetByNameSubstring("__None", morphs)
    return morphs

def GetGrayscale(morphs):
    # use GetByNameWithWithoutSubstring([], ["__None","__TakesColor"], morphs)
    return morphs

def GetRGB(morphs):
    # use GetByNameSubstring("__TakesColor", morphs)
    return [mesh]

def CreateVariant(object):
    pass

def AddVariants(layer):
    print("Add Variants")
    # Add variants to the layer
    for i in range(0, len(layer)):
        if "__Variants_" in layer[i].name:
            n = IntAfterSubstring(layer[i].name, "__Variants_")
            print("Variants: " + str(n))
        continue
    print("End Add Variants")

def CreateBakeTargets():
    print("Create Bake Targets")
    # morphs are meshes based on input object with shape keys
    morphs = GetMorphObject()
    # A list of meshes that are not shaded
    unshaded_group = GetUnshaded(morphs)
    # A list of meshes that are shaded but with no color
    grayscale_group = GetGrayscale(morphs)
    # A list of meshes that are shaded and with color
    rgb_group = GetRGB(morphs)
    rgb_layer = rgb_group
    AddVariants(rgb_layer)
    print("End Create Bake Targets")