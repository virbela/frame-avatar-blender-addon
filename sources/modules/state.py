try:
    import bpy
except ImportError:
    import modules.mocks.bpy_mock as bpy

import modules.data_classes as dc

# Pieces of State
rgb_layer = []
r_layer = []
g_layer = []
b_layer = []

ui = {}

ao_textures = {}
paint_textures = {}

# Accessors and Mutators
def add_ao_texture(ao_tex : dc.AOTexture) -> None:
    """
    Add an AO texture to the dictionary.
    """
    global ao_textures
    ao_textures[ao_tex.name] = ao_tex

def add_paint_texture(paint_tex : dc.PaintTexture) -> None:
    """
    Add a paint texture to the dictionary.
    """
    global paint_textures
    paint_textures[paint_tex.name] = paint_tex
    
def set_ui(data: dict) -> None:
    """
    Set the UI value.
    """
    global ui
    ui = data

def set_ui_prop(key : str, value) -> None:
    """
    Set the UI prop value.
    """
    global ui
    ui[key] = value

def get_ui() -> dict:
    """
    Get the UI.
    """
    return ui



def set_rgb_layer(layer : list ) -> None:
    """
    Set the RGB layer to the given list of colors.
    """
    global rgb_layer
    rgb_layer = layer

def set_r_layer(layer : list) -> None:
    """
    Set the R layer to the given list of colors.
    """
    global r_layer
    r_layer = layer 

def set_g_layer(layer : list) -> None:
    """
    Set the G layer to the given list of colors.
    """
    global g_layer
    g_layer = layer

def set_b_layer(layer : list) -> None:
    """
    Set the B layer to the given list of colors.
    """
    global b_layer
    b_layer = layer

def get_rgb_layer() -> list:
    """
    Get the RGB layer.
    """
    return rgb_layer

def get_r_layer() -> list:
    """
    Get the R layer.
    """
    return r_layer

def get_g_layer() -> list:
    """
    Get the G layer.
    """
    return g_layer

def get_b_layer() -> list:
    """
    Get the B layer.
    """
    return b_layer

def extend_rgb_layer(lst : list) -> None:
    """
    Extend the RGB layer.
    """
    global rgb_layer
    rgb_layer.extend(lst)

def extend_r_layer(lst : list) -> None:
    """
    Extend the R layer.
    """
    global r_layer
    r_layer.extend(lst)

def extend_g_layer(lst : list) -> None:
    """
    Extend the G layer.
    """
    global g_layer
    g_layer.extend(lst)

def extend_b_layer(lst : list) -> None:
    """
    Extend the B layer.
    """
    global b_layer
    b_layer.extend(lst)




