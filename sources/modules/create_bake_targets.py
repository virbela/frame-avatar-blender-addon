from utils.string_utils import GetByNameSubstring

def GetMorphObject():
    return []

def GetUnshaded(morphs):
    return morphs

def GetGrayscale(morphs):
    return morphs

def GetRGB(morphs):
    return morphs

def CreateBakeTargets():
    print("Create Bake Targets")
    
    morphs = GetMorphObject()
    unshaded_group = GetUnshaded(morphs)
    grayscale_group = GetGrayscale(morphs)
    rgb_group = GetRGB()