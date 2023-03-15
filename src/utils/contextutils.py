import bpy
from contextlib import contextmanager

from .helpers import is_reference_valid

@contextmanager
def active_scene(name: str):
    active_scene = bpy.context.scene

    # -- set new active scene
    new_scene = bpy.data.scenes.get(name) or bpy.data.scenes.new(name)
    bpy.context.window.scene = new_scene

    yield

    # -- restore previous active scene
    bpy.context.window.scene = active_scene


@contextmanager
def selection(objects: list[bpy.types.Object] = None, view_layer: bpy.types.ViewLayer = None):
    selected = [o for o in bpy.data.objects if o.select_get()]

    # -- clear old selection state
    for obj in selected:
        obj.select_set(False)

    # -- set new selection state
    if objects:
        for obj in objects:
            obj.select_set(True, view_layer=view_layer)

    yield

    # -- clear new selection state
    if objects:
        for obj in objects:
            if is_reference_valid(obj):
                obj.select_set(False, view_layer=view_layer)

    # -- restore old selection state
    for obj in selected:
        if is_reference_valid(obj):
            obj.select_set(True, view_layer=view_layer)

@contextmanager
def active_object(object: bpy.types.Object = None, view_layer: bpy.types.ViewLayer = None):
    active = view_layer.objects.active

    # -- set current active
    view_layer.objects.active = object

    yield

    # -- restore old active
    view_layer.objects.active = active
